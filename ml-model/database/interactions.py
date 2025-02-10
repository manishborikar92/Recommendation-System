"""
database/interactions.py

This module provides functions for dynamically creating user-specific interaction tables,
logging user events, and retrieving recent user interactions using asyncpg for asynchronous,
non-blocking database access.
"""
import os
import asyncpg
import logging
from typing import Optional, List
from asyncpg import Record
from dotenv import load_dotenv

load_dotenv()

# Import database settings from the config file.
# Ensure that config/settings.py defines DATABASE_URL, e.g.,
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
# from config.settings import DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

# Remove the '+asyncpg' suffix if present; asyncpg expects "postgresql://" or "postgres://" scheme.
if DATABASE_URL.startswith("postgresql+asyncpg"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql", 1)

logger = logging.getLogger(__name__)


class DBInteractions:
    """
    A class to manage dynamic user interaction tables in PostgreSQL.
    For each unique user_id, a table named '{user_id}_interactions' is created (if not exists)
    to store events with the following schema:
        (event_type TEXT, product_id VARCHAR(10), query TEXT, timestamp TIMESTAMP)
    """

    _pool: Optional[asyncpg.pool.Pool] = None

    @classmethod
    async def init_pool(cls) -> None:
        """
        Initialize the asyncpg connection pool.
        Should be called once at application startup.
        """
        if cls._pool is None:
            try:
                cls._pool = await asyncpg.create_pool(dsn=DATABASE_URL)
                logger.info("Database pool created successfully.")
            except Exception as e:
                logger.exception("Failed to create database pool: %s", e)
                raise

    @classmethod
    async def close_pool(cls) -> None:
        """
        Close the asyncpg connection pool.
        Should be called during application shutdown.
        """
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            logger.info("Database pool closed.")

    @classmethod
    async def create_user_table(cls, user_id: str) -> None:
        """
        Ensures that the interaction table for a given user exists.
        The table name is constructed as '{user_id}_interactions'. This method assumes that
        the provided user_id has already been validated (e.g. matches r'^[a-zA-Z0-9]{1,50}$').
        
        :param user_id: The unique identifier for the user.
        """
        # Note: The table name is directly interpolated since user_id is expected to be validated.
        table_name = f"{user_id}_interactions"
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            event_type TEXT NOT NULL,
            product_id VARCHAR(10),
            query TEXT,
            timestamp TIMESTAMP NOT NULL DEFAULT NOW()
        );
        """
        async with cls._pool.acquire() as connection:
            try:
                await connection.execute(query)
                logger.debug("Ensured table '%s' exists.", table_name)
            except Exception as e:
                logger.exception("Error creating table '%s': %s", table_name, e)
                raise

    @classmethod
    async def log_interaction(
        cls,
        user_id: str,
        event_type: str,
        product_id: Optional[str] = None,
        query_text: Optional[str] = None,
    ) -> None:
        """
        Logs a user interaction event into the user's interaction table.
        This function first ensures the table exists, then inserts the event record.
        
        :param user_id: The user's unique identifier.
        :param event_type: The type of event (e.g., "product_click", "search_query").
        :param product_id: The product ID (required for "product_click" events; must be 10 uppercase alphanumeric characters).
        :param query_text: The search query text (required for "search_query" events).
        """
        # Create the user-specific table if it does not exist
        await cls.create_user_table(user_id)
        table_name = f"{user_id}_interactions"
        insert_sql = f"""
        INSERT INTO {table_name} (event_type, product_id, query, timestamp)
        VALUES ($1, $2, $3, NOW());
        """
        async with cls._pool.acquire() as connection:
            try:
                await connection.execute(insert_sql, event_type, product_id, query_text)
                logger.info("Logged interaction for user '%s' with event '%s'.", user_id, event_type)
            except Exception as e:
                logger.exception("Error logging interaction for user '%s': %s", user_id, e)
                raise

    @classmethod
    async def fetch_user_interactions(cls, user_id: str, days: int = 30) -> List[Record]:
        """
        Fetches the user interactions for the given user within the past specified number of days.
        Returns an empty list if the user's interaction table does not exist.
        
        :param user_id: The user's unique identifier.
        :param days: Number of days in the past to fetch interactions (default is 30).
        :return: A list of asyncpg.Record objects representing the interaction events.
        """
        table_name = f"{user_id}_interactions"
        select_sql = f"""
        SELECT event_type, product_id, query, timestamp
        FROM {table_name}
        WHERE timestamp >= NOW() - INTERVAL '{days} days'
        ORDER BY timestamp DESC;
        """
        async with cls._pool.acquire() as connection:
            try:
                records = await connection.fetch(select_sql)
                logger.debug("Fetched %d interactions for user '%s'.", len(records), user_id)
                return records
            except asyncpg.exceptions.UndefinedTableError:
                logger.warning("Interaction table for user '%s' does not exist.", user_id)
                return []
            except Exception as e:
                logger.exception("Error fetching interactions for user '%s': %s", user_id, e)
                raise


# # If this module is run directly, demonstrate pool initialization.
# if __name__ == "__main__":
#     import asyncio

#     async def main():
#         await DBInteractions.init_pool()
#         try:
#             # Example usage: log an interaction and then fetch interactions.
#             user_id = "u679b62919e5adb348bd5616f"
#             await DBInteractions.log_interaction(
#                 user_id=user_id,
#                 event_type="product_click",
#                 product_id="B08CF3D7QR",
#             )
#             user_id = "u679b62919e5adb348bd5616f"
#             await DBInteractions.log_interaction(
#                 user_id=user_id,
#                 event_type="search_query",
#                 query_text="laptop keyboard under 500rs",
#             )
#             interactions = await DBInteractions.fetch_user_interactions(user_id)
#             for record in interactions:
#                 print(dict(record))
#         finally:
#             await DBInteractions.close_pool()

#     asyncio.run(main())
