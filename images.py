from typing import Union
from fastapi import FastAPI, Response
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


class Image(BaseModel):
    image_id: int
    q: Union[str, None] = None
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

    @field_validator("q")
    def check_q(cls, value):
        if value is not None and "gmail" in value:
            raise ValueError("Значение поля недопустимо")
        return value


app = FastAPI()


@app.get("/")
async def hello():
    return Response("<p>Hello World!</p>")


@app.get("/images/{image_id}/")
async def show_image(image_id: int, q: Union[str, None] = None,
                     email="loop@mail.ru") -> Image:
    return Image(image_id=image_id, q=q, email=email)


@app.put("/images/{image_id}/")
async def update_image(image_id: int, image: Image):
    return {"image_id": image_id, "image_email": image.email}
