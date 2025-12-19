from enum import Enum
from typing import Union, Optional, List
from pydantic import BaseModel, Field


class RegulatorySubcategoryEnum(str, Enum):
    PRIORITY = "priority"
    SPEED = "speed"
    MOVEMENT = "movement"
    PARKING = "parking"


class WarningSubcategoryEnum(str, Enum):
    ROAD_CONDITIONS = "road_conditions"
    INTERSECTIONS = "intersections"
    PEDESTRIAN = "pedestrian"
    WEATHER = "weather"


class InformationSubcategoryEnum(str, Enum):
    DIRECTION = "direction"
    SERVICES = "services"
    DISTANCES = "distances"
    FACILITIES = "facilities"


class Regulatory(BaseModel):
    name: str = Field(default="Panneaux réglementaires")
    description: str = Field(
        default="Panneaux informant les usagers de la route des lois et réglementations de circulation")
    subcategory: RegulatorySubcategoryEnum


class Warning(BaseModel):
    name: str = Field(default="Panneaux d'avertissement")
    description: str = Field(
        default="Panneaux avertissant les usagers des conditions dangereuses de la route")
    subcategory: WarningSubcategoryEnum


class Information(BaseModel):
    name: str = Field(default="Panneaux d'information")
    description: str = Field(
        default="Panneaux fournissant des informations sur les destinations, services et installations")
    subcategory: InformationSubcategoryEnum


class RoadSign(BaseModel):
    id: str
    name: str
    category: Union[Regulatory, Warning, Information]
    image: str
    description: str
    rules: List[str]
    typical_locations: List[str]
    shape: Optional[str] = None
    common_mistakes: Optional[List[str]] = None

    def clean(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.name,
            "description": self.description,
            "rules": self.rules,
            "typical_locations": self.typical_locations,
            "shape": self.shape,
            "common_mistakes": self.common_mistakes,
        }


class RoadSignList(BaseModel):
    signs: List[RoadSign]


class MCQ(BaseModel):
    question: str = Field(..., description="The quizz question")
    difficulty: str = Field(..., description="The quizz difficulty")
    options: list[str] = Field(..., description="answer candidates shuffled")
    answer: int = Field(..., description="index of the correct answer")
    explanation: str = Field(..., description="Explanation of the correct answer")


class MCQs(BaseModel):
    items: List[MCQ]


class MCQResponse(MCQ):
    id: str | int
