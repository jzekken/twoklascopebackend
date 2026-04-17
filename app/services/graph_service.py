import logging
from app.core.graph_db import neo4j_db

logger = logging.getLogger(__name__)


async def get_existing_skills_for_strand(strand_name: str) -> list[str]:
    """
    Fetches all existing skills under a specific strand to feed the Semantic Net.
    Prevents the AI from hallucinating duplicate skill names.
    """
    if not neo4j_db.driver:
        return []

    query = """
    MATCH (s:Strand {name: $strand_name})<-[:BELONGS_TO]-(t:Topic)
    RETURN t.name AS topic_name LIMIT 50
    """
    try:
        # AWAIT the query execution
        records, _, _ = await neo4j_db.driver.execute_query(
            query, strand_name=strand_name.upper())
        return [record["topic_name"] for record in records]
    except Exception as e:
        logger.error(f"Failed to fetch existing skills: {str(e)}")
        return []


async def get_user_skill_web(user_id: str) -> dict | None:
    """
    Queries Neo4j to build a complete Constellation profile of the user's learning journey.
    Pulls their overall XP distribution AND their highest-leveled specific skills.
    """
    if not neo4j_db.driver:
        return None

    # Query 1: Get overall XP distribution across the 4 main strands
    xp_query = """
    MATCH (u:User {id: $user_id})-[e:EXPLORED]->(s:Strand)
    RETURN s.name AS strand, e.total_xp AS xp
    """

    # Query 2: Get their highest leveled Skills/Topics (The RPG mechanic)
    skills_query = """
    MATCH (u:User {id: $user_id})-[m:MASTERED]->(t:Topic)
    RETURN t.name AS skill_name, m.count AS level
    ORDER BY level DESC LIMIT 5
    """

    try:
        # AWAIT both queries
        xp_records, _, _ = await neo4j_db.driver.execute_query(
            xp_query, user_id=user_id)
        skill_records, _, _ = await neo4j_db.driver.execute_query(
            skills_query, user_id=user_id)

        if not xp_records:
            return None

        xp_distribution = {record["strand"]: record["xp"]
                           for record in xp_records}
        top_skills = {record["skill_name"]: record["level"]
                      for record in skill_records}

        return {
            "xp_distribution": xp_distribution,
            "top_skills": top_skills
        }
    except Exception as e:
        logger.error(f"Failed to fetch Skill Web: {str(e)}")
        return None


async def save_skill_to_graph(user_id: str, strand_name: str, skill_name: str, xp_awarded: int) -> bool:
    """
    Saves the mastered skill to the Neo4j Skill Tree.
    Creates the nodes if they don't exist, and levels them up if they do.
    """
    if not neo4j_db.driver:
        return False

    query = """
    // 1. Find or Create the User (Fixed: Changed MATCH to MERGE)
    MERGE (u:User {id: $user_id})

    // 2. Ensure the Strand exists and update their overall Strand XP
    MERGE (s:Strand {name: $strand_name})
    MERGE (u)-[e:EXPLORED]->(s)
    ON CREATE SET e.total_xp = $xp_awarded
    ON MATCH SET e.total_xp = e.total_xp + $xp_awarded

    // 3. Ensure the Topic (Skill) exists and connect it to the Strand
    MERGE (t:Topic {name: $skill_name})
    MERGE (t)-[:BELONGS_TO]->(s)

    // 4. The RPG Mechanic: Link User to the Topic and Level it up!
    MERGE (u)-[m:MASTERED]->(t)
    ON CREATE SET m.count = 1
    ON MATCH SET m.count = m.count + 1
    
    RETURN u, s, t
    """

    try:
        # AWAIT the insert
        await neo4j_db.driver.execute_query(
            query,
            user_id=user_id,
            strand_name=strand_name.upper(),
            skill_name=skill_name,
            xp_awarded=xp_awarded
        )
        return True
    except Exception as e:
        logger.error(f"Failed to graph skill to Neo4j: {str(e)}")
        return False
