from graph.invoke_graph import invoke_graph
import requests
from requests.auth import HTTPBasicAuth
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

class Body(BaseModel):
    message: str
    session_id: str
    user_id: str


@app.post("/invoke")
def generate(body: Body):
    final_answer = invoke_graph(
        user_query=body.message,
        session_id=body.session_id,
        user_id=body.user_id
    )

    return {"response": final_answer}


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