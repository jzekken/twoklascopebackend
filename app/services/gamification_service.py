import logging
from supabase import Client
from fastapi import HTTPException
from app.schemas.scan import SaveScanRequest

logger = logging.getLogger(__name__)

# SECURITY OVERRIDE: The backend dictates points, never the client.
BASE_XP_PER_SCAN = 50


def save_user_discovery(db_client: Client, user_id: str, request: SaveScanRequest) -> str:
    """
    Saves the finalized scan, and triggers the Postgres RPC to update Streaks, XP, and the Skill Tree.
    """
    try:
        # 1. Calculate actual XP server-side
        final_xp = BASE_XP_PER_SCAN * \
            2 if request.is_aligned_with_compass else BASE_XP_PER_SCAN

        # 2. Prepare data for the 'scans' history table
        data = {
            "user_id": user_id,
            "object_name": request.object_name,
            "chosen_lens": request.chosen_lens,
            "image_url": request.image_url,
            "learning_deck": request.learning_deck,
            "xp_awarded": final_xp,  # Use the secure server calculated XP
            "is_aligned_with_compass": request.is_aligned_with_compass
        }

        # 3. Insert into the scans table
        response = db_client.table("scans").insert(data).execute()

        if not response.data:
            raise ValueError(
                "Insert succeeded but no data returned from Supabase.")

        scan_id = response.data[0]["id"]

        # 4. 🚀 CRITICAL: Execute the Postgres Function to update Streaks and Profile XP
        db_client.rpc(
            "award_xp_and_update_streak",
            {
                "p_user_id": user_id,
                "p_strand": request.chosen_lens,
                # The RPC handles the x2 multiplier internally based on the boolean!
                "p_base_xp": BASE_XP_PER_SCAN,
                "p_is_aligned": request.is_aligned_with_compass
            }
        ).execute()

        # Override the request object so downstream processes (like Neo4j) use the correct XP
        request.xp_awarded = final_xp

        return scan_id

    except Exception as e:
        logger.error(
            f"Failed to save scan to Supabase for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Database error while saving scan history."
        )
