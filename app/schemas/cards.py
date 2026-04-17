from pydantic import BaseModel, Field


class CardConcept(BaseModel):
    domain: str = Field(..., description="The official K-12/CHED Domain (e.g., 'Automotive Engineering', 'Philippine History')")
    skill: str = Field(..., description="The specific educational topic (e.g., 'Combustion Mechanics', 'Cultural Integration')")
    lesson_text: str = Field(
        ..., description="A short, punchy paragraph explaining the core concept based on the scanned object.")


class CardRealWorld(BaseModel):
    application_text: str = Field(
        ..., description="Explains how this concept is actually used in the real world in a Filipino context.")
    fun_fact: str = Field(
        ..., description="A highly shareable piece of trivia related to the object and the skill.")


class CardChallenge(BaseModel):
    question: str = Field(
        ..., description="A scenario-based multiple-choice question testing the lesson.")
    options: list[str] = Field(...,
                               description="Array of 3 to 4 possible answers.")
    correct_answer: str = Field(...,
                                description="The exact string of the correct option.")
    explanation: str = Field(...,
                             description="A short explanation of why the answer is correct.")


class LearningDeckRequest(BaseModel):
    object_name: str = Field(...,
                             description="The object the user scanned (e.g., 'Jeepney')")
    chosen_lens: str = Field(...,
                             description="The academic strand they clicked (e.g., 'STEM')")
    grade_level: str = Field(..., description="The user's academic stage")


class LearningDeckResponse(BaseModel):
    concept_card: CardConcept
    real_world_card: CardRealWorld
    challenge_card: CardChallenge
