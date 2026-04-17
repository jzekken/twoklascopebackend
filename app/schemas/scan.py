from pydantic import BaseModel, Field
from typing import Any


class SaveScanRequest(BaseModel):
    object_name: str = Field(...,
                             description="The primary name of the scanned object")
    chosen_lens: str = Field(...,
                             description="The strand chosen: STEM, ABM, HUMSS, or TVL")
    image_url: str = Field(...,
                           description="The public Supabase Storage URL for the history tab")
    learning_deck: dict[str, Any] = Field(...,
                                          description="The completed deck JSON payload")

    # We keep this for backward compatibility with the frontend, but the backend will ignore it for security.
    xp_awarded: int = Field(...,
                            description="Client requested XP (Will be overridden by backend)")

    # ADD THIS FIELD:
    is_aligned_with_compass: bool = Field(
        default=False,
        description="Whether this strand matches their top compass affinity"
    )


class SaveScanResponse(BaseModel):
    status: str
    message: str
    scan_id: str
    xp_awarded: int
