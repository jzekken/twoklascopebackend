from neo4j import AsyncGraphDatabase, AsyncDriver
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jConnection:
    def __init__(self):
        self.driver: AsyncDriver | None = None
        self.connect()

    def connect(self):
        if not settings.NEO4J_URI or not settings.NEO4J_PASSWORD:
            logger.warning(
                "Neo4j credentials missing. Graph features will be disabled.")
            return

        try:
            # Initialize the ASYNC driver
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
            )
            logger.info("Successfully initialized Async Neo4j AuraDB driver!")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            self.driver = None

    async def close(self):
        if self.driver:
            await self.driver.close()


# Instantiate globally
neo4j_db = Neo4jConnection()
