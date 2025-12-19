from fastapi import FastAPI

from src.utils import format_sign
from .modules.road import RoadSignModule

app = FastAPI(
    title="Road Sign",
    description="whatsapp chatbot to learn road signs",
    version="1.0.0"
)

road = RoadSignModule()

@app.get("/sign-quizz")
async def sign_quizz(phone:str, level:str="2"):
    quizz = await road.gen_sign_quizz(phone, level)
    qts = [f"{i+1}) {q}" for i, q in enumerate(quizz.options)]

    return {
        "text":f"{quizz.question}\n\n{"\n".join(qts)}",
        "buttons" : [
            {
                "id": f"{i}",
                "label":f"Option {i+1}",
                "description": q[:71]
            }
            for i, q in enumerate(quizz.options)
        ],
        "answer":f"{quizz.answer}",
        "explanation": quizz.explanation
    }


@app.get("/general-quizz")
async def general_quizz(phone:str, level:str="2"):
    quizz = await road.gen_quizz(phone, level)
    qts = [f"{i+1}) {q}" for i, q in enumerate(quizz.options)]

    return {
        "text":f"{quizz.question}\n\n{"\n".join(qts)}",
        "buttons" : [
            {
                "id": f"{i}",
                "label":f"Option {i+1}",
                "description": q[:71]
            }
            for i, q in enumerate(quizz.options)
        ],
        "answer":f"{quizz.answer}",
        "explanation": quizz.explanation
    }


@app.get("/learn-sign")
async def gen_quizz(phone:str):
    sign = await road.learn_sign(phone)
    return {
        "text": format_sign(sign),
        "image": sign.image
    }
