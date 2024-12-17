from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
from app.core.config import settings

class Database:
    mongodb_client: Optional[AsyncIOMotorClient] = None
    redis_client: Optional[Redis] = None

    @classmethod
    async def connect_to_mongodb(cls) -> None:
        """Connect to MongoDB."""
        try:
            cls.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL, username=settings.MONGODB_USER, password=settings.MONGODB_PASSWORD)
            # Ping the server to validate connection
            await cls.mongodb_client.admin.command('ping')
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise

    @classmethod
    def connect_to_redis(cls) -> None:
        """Connect to Redis."""
        try:
            cls.redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
            # Ping the server to validate connection
            cls.redis_client.ping()
            print("Successfully connected to Redis")
        except Exception as e:
            print(f"Error connecting to Redis: {e}")
            raise

    @classmethod
    async def close_mongodb_connection(cls) -> None:
        """Close MongoDB connection."""
        if cls.mongodb_client:
            cls.mongodb_client.close()
            cls.mongodb_client = None
            print("MongoDB connection closed")

    @classmethod
    def close_redis_connection(cls) -> None:
        """Close Redis connection."""
        if cls.redis_client:
            cls.redis_client.close()
            cls.redis_client = None
            print("Redis connection closed")

    @classmethod
    async def init_mongodb(cls) -> None:
        """Initialize MongoDB connection and create collections if they don't exist."""
        try:
            await cls.connect_to_mongodb()
            
            # Define your collections here
            required_collections = ['flights']  # Add your collection names
            
            # Get existing collections
            db = cls.mongodb_client[settings.MONGODB_DB_NAME]
            existing_collections = await db.list_collection_names()
            
            # Create missing collections
            for collection in required_collections:
                if collection not in existing_collections:
                    await db.create_collection(collection)
                    print(f"Created collection: {collection}")
            
            print("MongoDB initialization completed")
            
        except Exception as e:
            print(f"Error initializing MongoDB: {e}")
            raise

    @classmethod
    async def init_redis(cls) -> None:
        """Initialize Redis connection and set up any required keys."""
        try:
            cls.connect_to_redis()
            
            # Initialize any default Redis keys/values if needed
            if not cls.redis_client.exists("api_version"):
                cls.redis_client.set("api_version", "1.0")
            
            print("Redis initialization completed")
            
        except Exception as e:
            print(f"Error initializing Redis: {e}")
            raise


# Helper methods to get database connections
def get_mongodb() -> AsyncIOMotorClient:
    return Database.mongodb_client

def get_redis() -> Redis:
    return Database.redis_client