from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.core.config import settings
from app.schemas.chat import ChatRequest
from fastapi import HTTPException

# Keep temperature low for factual, focused tutoring
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.4
)


async def generate_tutor_response(data: ChatRequest) -> str:
    try:
        # 1. Establish the core persona WITH dynamic context injected
        system_prompt = (
            "You are the Tuklascope AI Tutor, a friendly, culturally-aware Filipino educational guide. "
            f"The student is currently looking at a scanned object: '{data.object_name}' "
            f"through the lens of the '{data.strand}' academic strand.\n\n"
            f"They are specifically reading this learning card:\n\"{data.card_content}\"\n\n"
            "Answer their questions accurately based ONLY on this context and the K-12 DepEd curriculum. "
            "Explain concepts simply, clearly, and directly. Use a supportive and encouraging tone. "
            "Do not hallucinate information outside of this scope."
        )

        messages = [SystemMessage(content=system_prompt)]

        # 2. Rebuild the conversation history for context continuity
        for msg in data.history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))

        # 3. Append the brand new question
        messages.append(HumanMessage(content=data.message))

        # 4. Invoke the model
        response = await llm.ainvoke(messages)

        return response.content

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Tutor AI Processing Error: {str(e)}")
