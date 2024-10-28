import asyncio
import json

from aiohttp import ClientSession, web
from aiologger import Logger
from aiologger.formatters.base import Formatter

logger = Logger.with_default_handlers(
    level="DEBUG",
    formatter=Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)


async def get_weather(city):
    async with ClientSession() as session:
        url = "http://api.weatherapi.com/v1/current.json"
        params = {"q": city, "key": "4d79ec42d5714f0b84070805242710"}

        async with session.get(url=url, params=params) as response:
            weather_json = await response.json()
            if response.status == 200:
                return weather_json["current"]["condition"]["text"]
            elif response.status == 401:
                return weather_json["message"]
            else:
                return weather_json["error"]["message"]


async def get_translation(text, source, target):
    async with ClientSession() as session:
        url = "https://libretranslate.de/translate"

        data = {"q": text, "source": source, "target": target, "format": "text"}

        async with session.post(url, json=data) as response:
            if response.status == 200:
                try:
                    translate = (await response.json())["translatedText"]
                except KeyError:
                    await logger.error(
                        f"Невозможно получить перевод для слова: {text}")
                    translate = text
            else:
                await logger.error(await response.text())
                translate = text
            return translate


async def handle(request):
    city = request.rel_url.query["city"]

    await logger.info(f"Поступил запрос на город: {city}")

    weather = await get_translation(await get_weather(city), "en", "ru")
    result = {"city": city, "weather": weather}

    return web.Response(body=json.dumps(result, ensure_ascii=False),
                        content_type="text/json")


async def main():
    app = web.Application()
    app.add_routes([web.get("/weather", handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8000)
    await site.start()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
