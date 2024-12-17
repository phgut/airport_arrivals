import logging
import json
from collections import defaultdict
from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
from app.core.database import Database
from app.integration.flightio import FlightETL
from app.core.database import get_mongodb, get_redis
from app.core.config import settings
from datetime import datetime

router = APIRouter()

flight_etl = FlightETL()

# Response model
class FlightCount(BaseModel):
    country: str
    flightCount: int

# Use cache settings from config
CACHE_KEY = settings.FLIGHT_SEARCH_CACHE_KEY
CACHE_EXPIRY = settings.FLIGHT_SEARCH_CACHE_EXPIRY

@router.post('/redis/clear')
async def clear_redis():
    redis = get_redis()
    redis.flushall()
    return {"message": "Redis cache cleared"}

@router.get("/search", response_model=List[FlightCount])
async def search_flights(
    term: Optional[str] = Query(None, description="Search term for country"),
):
    mongodb = get_mongodb()
    redis = get_redis()
    if len(term) != 3:
        return []
    
    try:
        term = term.upper()
        logging.info(f"Key: {flight_etl.get_cache_key(term)}")

        # 1. Check Redis cache first
        data = await check_redis_cache(redis, term)
        if not data:
            data = await check_mongodb(mongodb, term)
            if data:
                logging.info("Data found in MongoDB")
                await flight_etl.set_redis_cache(term, data)
            else:
                logging.info("Running ETL process")
                data = await run_etl(term)
        else:
            logging.info("Data found in Redis cache")
        if data is None:
            return []
        counter = defaultdict(int)
        for item in data['flights']:
            counter[item['source_country']] += 1
        return [FlightCount(country=country, flightCount=count) for country, count in counter.items()]

    except Exception as e:
        logging.error(f"Error in search_flights: {e}")
        raise

async def check_redis_cache(redis: Redis, term: Optional[str]):
    """Check if data exists in Redis cache."""
    cache_key = flight_etl.get_cache_key(term)
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

async def check_mongodb(mongodb: AsyncIOMotorClient, term: Optional[str]):
    """Query MongoDB for flight data."""
    collection = mongodb.flight_db.flights
    key = flight_etl.get_cache_key(term)
    query = {"key": {"$regex": key, "$options": "i"}} if key else {}
    
    cursor = collection.find(query)
    results = await cursor.to_list()
    
    if results:
        return results
    return None

async def run_etl(term: Optional[str]):
    """Run the ETL process to fetch new data."""
    # Implement your ETL logic here or call your flightio.py
    etl_data = flight_etl.run_etl(iata=term)
    return etl_data