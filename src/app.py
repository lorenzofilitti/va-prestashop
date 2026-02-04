from typing import Optional

import requests
from requests.auth import HTTPBasicAuth
from fastapi import FastAPI
from pydantic import BaseModel

from src.llms.core import Core
from src.llms.base_llm import LlmSettings

app = FastAPI()

class Body(BaseModel):
    message: str
    conversation_id: str


@app.post("/generate")
def generate(body: Body):
    resp: dict = Core(settings=LlmSettings(
        model="llama3.2"
    )).generate_answer(body.message)


    requests.post(f"http://localhost:8080/api/carts/{user_id}")


    return {"response": f"{resp['response']}!"}


@app.get("/cart")
def cart():
    resp = requests.get("http://127.0.0.1:8000/api/cart", auth=HTTPBasicAuth("SEXH9MJL5QHYH64KN7AXAKYD7STRUDZJ", ""))
    return {"response": f"{resp.text}"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )