import json
import uuid
import asyncio
import functools
from typing import List
from pathlib import Path
from random import shuffle, choice
from datetime import datetime
# locale modules
from src.utils import select_items
from .database import DatabaseAPI
from .agent.prompt import (
    QUIZZER_PROMPT,
    SIGN_QUIZZER_PROMPT,
    RECOGNIZER_PROMPT
)
from .agent import agent, AgentDeps
from .types import RoadSign, MCQs, MCQResponse


DEFAULT_PATH = str(Path(__file__).parents[1] / "data.json")


class RoadSignModule:
    def __init__(self, path: str = DEFAULT_PATH):
        with open(path, "r", encoding="utf8") as f:
            self.signs = [RoadSign(**r) for r in json.load(f)]

        self.by_id = {r.id: r for r in self.signs}
        self.by_category = {}
        for sign in self.signs:
            cat = self.by_category.get(sign.category.name, [])
            cat.append(sign)

        self.api = DatabaseAPI()

    def get_by_id(self, ids: List[str]) -> List[RoadSign]:
        return [self.by_id[i] for i in ids]

    @functools.lru_cache()
    def get_by_category(self, category: str) -> List[RoadSign]:
        return self.by_category.get(category, [])

    @property
    @functools.lru_cache()
    def ids(self):
        return list(self.by_id.keys())

    async def learn_sign(self, phone: str, cat: str = "") -> RoadSign:
        viewed = await self.api.get_viewed_signs(phone) or []
        choices = [r.id for r in self.get_by_category(cat)] if cat else self.ids
        choice_ids = select_items(choices, viewed, 1)
        sign = self.get_by_id(choice_ids)[0]
        asyncio.create_task(self.api.add_viewed_sign(phone, [*viewed, sign.id]))
        return sign

    async def _get_quizz(self, prompt_tmp, **kwargs) -> MCQs:
        result = await agent.run(
            deps=AgentDeps(
                    system_promt=prompt_tmp,
                    args={**kwargs, "date":datetime.now()}
                ),
            output_type=MCQs
        )
        return result.output

    async def gen_quizz(self, phone: str, level: str) -> MCQResponse:
        history = await self.api.get_user_quizz(phone, "general")
        history = "\n".join([str(q) for q in history])
        output = await self._get_quizz(
            QUIZZER_PROMPT, history=history, level=level
        )
        question = choice(output.items)
        asyncio.create_task(self.api.add_user_quizz(
            row_id:=str(uuid.uuid4()),
            phone, question.question,
            question.difficulty,
            "general"
        ))
        return MCQResponse(id=row_id, **question.model_dump())

    async def gen_sign_quizz(self, phone: str, level: str) -> MCQResponse:
        viewed = await self.api.get_viewed_signs(phone) or []
        choice_ids = [*viewed, *list(set(self.ids)-set(viewed))[:3]]
        # shuffle
        shuffle(choice_ids)
        signs = [r.clean() for r in self.get_by_id(choice_ids)]
        history = "\n\n".join([str(q) for q in signs])
        output = await self._get_quizz(
            SIGN_QUIZZER_PROMPT, history=history, level=level
        )
        question = choice(output.items)
        asyncio.create_task(self.api.add_user_quizz(
            row_id:=str(uuid.uuid4()),
            phone, question.question,
            question.difficulty,
            "sign"
        ))
        return MCQResponse(id=row_id, **question.model_dump())

    async def recognize_sign(self, img: str):
        result = await agent.run(
            deps=AgentDeps(
                    system_promt=RECOGNIZER_PROMPT,
                args={"img":img}
                ),
        )
        return result.output

    async def update_response(self, id: str):
        await self.api.set_quizz_answer(id, True)
