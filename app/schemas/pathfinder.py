from pydantic import BaseModel, Field


class CareerPath(BaseModel):
    path_type: str = Field(
        ..., description="Must be one of: 'The Specialist', 'The Interdisciplinary', or 'The Object-Driven'")
    title: str = Field(..., description="The name of the college degree or career track (e.g., BS Food Technology)")
    description: str = Field(
        ..., description="A short, inspiring explanation of why this fits their unique web of skills and objects.")
    match_confidence: int = Field(
        ..., description="A percentage (0-100) indicating how well this matches their profile.")


class PathfinderResponse(BaseModel):
    profile_summary: str = Field(
        ..., description="A one-sentence summary of the student's unique learning profile.")
    recommendations: list[CareerPath] = Field(
        ..., description="Exactly 3 recommendations following the 3-Tiered strategy.")
