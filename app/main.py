from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api_router import api_router
from app.core.database import supabase_db
from app.core.graph_db import neo4j_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# SECURE CORS Configuration (UPDATED FOR MOBILE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is highly operational."}

# Database connection test route


@app.get("/health/db")
def db_health_check():
    try:
        # A simple ping to the auth service to check connectivity
        supabase_db.auth.get_session()
        return {"status": "ok", "message": "Successfully connected to Supabase!"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database connection failed: {str(e)}")


@app.get("/health/graph")
def graph_health_check():
    if not neo4j_db.driver:
        raise HTTPException(
            status_code=503, detail="Neo4j connection is not initialized.")

    try:
        # A simple Cypher query to ask Neo4j to return the number 1
        records, summary, keys = neo4j_db.driver.execute_query(
            "RETURN 1 AS status")
        if records and records[0]["status"] == 1:
            return {"status": "ok", "message": "Successfully mapped to the Neo4j Matrix!"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Neo4j connection failed: {str(e)}")
