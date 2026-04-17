import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.core.config import settings
from app.schemas.discover import DiscoverResponse, DiscoverRequest
from app.schemas.pathfinder import PathfinderResponse
from app.schemas.cards import LearningDeckResponse

# ==========================================
# 1. GLOBAL LLM INITIALIZATION
# ==========================================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.7
)

# Bind Pydantic models globally to prevent latency/overhead on every API call
structured_discover = llm.with_structured_output(DiscoverResponse)
structured_pathfinder = llm.with_structured_output(PathfinderResponse)
structured_deck = llm.with_structured_output(LearningDeckResponse)

# ==========================================
# 2. SERVICE FUNCTIONS
# ==========================================


async def generate_discovery_cards(data: DiscoverRequest) -> DiscoverResponse:
    try:
        prompt_text = (
            f"You are a Filipino educational guide. The user scanned a '{data.scanned_object}' "
            f"and is in the '{data.grade_level.value}' academic stage. Generate 4 culturally-relevant "
            "'Teaser Doors' representing the STEM, ABM, HUMSS, and TVL academic strands "
            f"based on this object, tailored specifically to a {data.grade_level.value} student."
        )
        return await structured_discover.ainvoke(prompt_text)
    except Exception as e:
        # Raise native python error; Router handles HTTP formatting
        raise RuntimeError(f"Text Discovery Generation Failed: {str(e)}")


async def generate_discovery_from_image(image_bytes: bytes, grade_level: str) -> DiscoverResponse:
    try:
        # Encode the image bytes to base64 for secure transport to Gemini
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt_text = (
            f"You are a Filipino educational guide. The user is in the '{grade_level}' academic stage. "
            "Look at the uploaded image and identify the primary object. Then, generate 4 culturally-relevant "
            "'Teaser Doors' representing the STEM, ABM, HUMSS, and TVL academic strands based on that specific object, "
            f"tailored to the comprehension level of a {grade_level} student. "
            "Accurately fill in the 'scanned_object' field with the name of the object you identified."
        )

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                }
            ]
        )

        return await structured_discover.ainvoke([message])
    except Exception as e:
        raise RuntimeError(f"AI Vision Processing Failed: {str(e)}")


async def generate_holistic_pathfinder(xp_distribution: dict, top_skills: dict) -> PathfinderResponse:
    try:
        prompt_text = (
            "You are a visionary Filipino Career Guidance Counselor. "
            "A student has been building an RPG-style academic Skill Tree. Here is their entire profile:\n"
            f"- Strand XP Distribution: {xp_distribution}\n"
            f"- Leveled-Up Skills: {top_skills}\n\n"
            "Analyze this ENTIRE constellation of data. Generate exactly 3 highly personalized college degree or career recommendations in the Philippines.\n\n"
            "CRITICAL RULE: DO NOT focus on just one specific strand or one specific skill. "
            "Every single recommendation MUST be a 'Synthesis Career'—a path that requires the combination of their diverse skills.\n\n"
            "Follow these 3 Synthesis Archetypes:\n"
            "1. 'The Integrator': A career that perfectly blends their top technical skills with their top social/business skills.\n"
            "2. 'The Problem-Solver': A career that uses their unique combination of skills to solve a specific, real-world issue in the Philippines.\n"
            "3. 'The Trailblazer': An emerging or modern career path where their specific web of skills gives them a unique, unfair advantage.\n\n"
            "In your descriptions, explicitly mention HOW the combination of their different skills makes them perfect for this role."
        )

        return await structured_pathfinder.ainvoke(prompt_text)
    except Exception as e:
        raise RuntimeError(f"Pathfinder AI Failed: {str(e)}")


async def generate_learning_deck(object_name: str, strand: str, grade_level: str, existing_skills: list[str]) -> LearningDeckResponse:
    try:
        prompt_text = (
            f"You are a Filipino educational guide writing for a {grade_level} student. "
            f"The user scanned a '{object_name}' and selected the '{strand}' academic strand. "
            "Generate a 3-Card Learning Deck (Concept, Real World, and Challenge).\n\n"
            "DATA GOVERNANCE RULE for the 'domain' and 'skill' fields:\n"
            f"1. You MUST categorize the 'domain' under an official {strand} discipline (e.g., 'Mechanical Engineering', 'Sociology', 'Accounting').\n"
            f"2. Here are the specific skills already in our database for {strand}: {existing_skills}\n"
            "3. If the core concept matches an existing skill conceptually, YOU MUST USE THE EXACT EXISTING SKILL STRING. "
            "Only invent a new skill name if it is fundamentally different."
        )

        return await structured_deck.ainvoke(prompt_text)
    except Exception as e:
        raise RuntimeError(f"Learning Deck AI Failed: {str(e)}")
