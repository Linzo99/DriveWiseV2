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

    async def gen_quizz(self, phone: str, level: str, quiz_type: str = "general") -> MCQResponse:
        """
        Generate a quiz question (general or sign-specific)
        
        Args:
            phone: User phone identifier
            level: Difficulty level (1-5)
            quiz_type: "general" or "sign"
        """
        # Get quiz history for the specific type
        quiz_history = await self.api.get_user_quizz(phone, quiz_type)
        questions_history = "\n".join([f"  * {q.get('question', '')}" for q in quiz_history[:3]])
        
        # Get learned signs (for context in both quiz types)
        viewed_signs = await self.api.get_viewed_signs(phone) or []
        learned_signs_context = "Aucun panneau appris pour le moment."
        
        if viewed_signs:
            # Get details of learned signs for context
            learned_signs = [r.clean() for r in self.get_by_id(viewed_signs[:10])]
            learned_signs_context = "\n".join([
                f"  * {sign.get('name', '')} ({sign.get('id', '')}): {sign.get('description', '')[:80]}"
                for sign in learned_signs
            ])
        
        if quiz_type == "sign":
            # Sign quiz: use last 3 viewed signs as context
            choice_ids = viewed_signs[-10:]
            signs = [r.clean() for r in self.get_by_id(choice_ids)]
            signs_history = "\n".join([f"   * {sign.get('name', '')} ({sign.get('id', '')}): {sign.get('description', '')[:80]}" for sign in signs])
            
            output = await self._get_quizz(
                SIGN_QUIZZER_PROMPT,
                history=signs_history,
                latest_questions=questions_history,
                level=level
            )
        else:
            # General quiz: use question history + learned signs for context
            output = await self._get_quizz(
                QUIZZER_PROMPT,
                history=questions_history,
                learned_signs=learned_signs_context,
                level=level
            )
        
        question = choice(output.items)
        asyncio.create_task(self.api.add_user_quizz(
            row_id:=str(uuid.uuid4()),
            phone, question.question,
            question.difficulty,
            quiz_type
        ))
        return MCQResponse(id=row_id, **question.model_dump())

    async def gen_sign_quizz(self, phone: str, level: str) -> MCQResponse:
        """Convenience method for sign quiz"""
        return await self.gen_quizz(phone, level, quiz_type="sign")

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
