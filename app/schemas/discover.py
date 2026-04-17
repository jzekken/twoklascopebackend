from pydantic import BaseModel, Field
from enum import Enum


class GradeLevel(str, Enum):
    ELEM = "Elementary (Grades 4-6)"
    JHS = "JHS (Grades 7-10)"
    SHS = "SHS (Grades 11-12)"


class TeaserDoor(BaseModel):
    lens: str = Field(...,
                      description="The track lens: STEM, ABM, HUMSS, or TVL")
    title: str = Field(...,
                       description="A catchy title for this specific discovery")
    teaser_text: str = Field(...,
                             description="A short, engaging explanation of the concept")
    estimated_xp: int = Field(
        default=50, description="XP rewarded for engaging with this door")


class DiscoverRequest(BaseModel):
    scanned_object: str = Field(..., example="Jeepney")
    grade_level: GradeLevel = Field(..., example="JHS (Grades 7-10)")


class DiscoverResponse(BaseModel):
    scanned_object: str
    grade_level: GradeLevel
    teaser_doors: list[TeaserDoor]
