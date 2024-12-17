import requests
import json
import os
from datetime import datetime
from collections import defaultdict
import pytz
from typing import Dict, List
import logging
from app.core.database import get_mongodb, get_redis
from app.core.config import settings

class FlightETL:
    def __init__(self):
        # API Configuration from settings
        self.API_KEY = settings.FLIGHTIO_API_KEY
        self.BASE_URL = settings.FLIGHTIO_BASE_URL
        
        # Database Configuration from settings
        self.MONGO_COLLECTION = settings.FLIGHTIO_MONGO_COLLECTION
        self.redis_client = None
        self.mongo_client = None
        # Initialize logger
        self.logger = logging.getLogger(__name__)

    def get_cache_key(self, iata: str, mode: str="arrivals", day: str=datetime.now(pytz.UTC).strftime('%Y-%m-%d')):
        return f"flight_data:{mode}:{iata}:{day}"
    
    def set_redis_cache(self, key: str, data: Dict):
        self.redis_client.set(key, json.dumps(data), int(settings.FLIGHTIO_REDIS_TTL))
    
    def init_redis(self):
        if not self.redis_client:
            self.redis_client = get_redis()
        print("redis_client", self.redis_client)
    
    def init_mongodb(self):
        if not self.mongo_client:
            self.mongo_client = get_mongodb()
        print("mongo_client", self.mongo_client)
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FlightETL, cls).__new__(cls)
        return cls.instance

    def extract(self, iata: str, mode: str="arrivals", day: str="1") -> Dict:
        """Extract data from flight API"""

        # If not in cache, fetch from API
        try:
            url = f"{self.BASE_URL}/compschedule/{self.API_KEY}"
            params = {
                "mode": mode,
                "day": day,
                "iata": iata
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            self.logger.info("Data successfully extracted from API")
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise

    def transform(self, raw_data: Dict, iata: str, mode: str, day: str) -> List[Dict]:
        """Transform raw flight data into desired format"""
        transformed_data = defaultdict(list)
        
        try:

            for data in raw_data:
                arrivals = data['airport']['pluginData']['schedule']['arrivals']['data']
                
                for flight in arrivals:
                    # Convert timestamp to datetime
                    timestamp = flight['flight']['time']['scheduled']['arrival']
                    utc_time = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
                    
                    transformed_flight = {
                        'source_country': flight['flight']['airport']['origin']['position']['country']['name'],
                        'source_iata': flight['flight']['airport']['origin']['code']['iata'],
                        'destination_iata': iata,
                        'arrival_time_utc': utc_time.isoformat(),
                        'arrival_date_utc': utc_time.date().isoformat(),
                        'flight_number': flight['flight']['identification']['number']['default'],
                    }
                    transformed_data[utc_time.date().isoformat()].append(transformed_flight)
            
            with open('transformed_data.json', 'w') as f:
                json.dump(transformed_data, f)
            self.logger.info(f"Transformed {len(transformed_data)} flight records")
            return transformed_data
            
        except KeyError as e:
            self.logger.error(f"Data transformation failed: {str(e)}")
            raise

    def load(self, transformed_data: List[Dict], iata: str, mode: str, day: str):
        """Load transformed data into MongoDB"""
        try:
            db = self.mongo_client[settings.MONGODB_DB_NAME]
            collection = db[self.MONGO_COLLECTION]
            response = None
            today = datetime.fromtimestamp(datetime.now().timestamp(), tz=pytz.UTC).date().isoformat()

            for date, flights in transformed_data.items():
                key = self.get_cache_key(iata, mode, date)
                # Create a single document with the key and all transformed data
                document = {
                    'key': key,
                    'flights': flights,
                }
            
                # Insert or update the single document
                collection.update_one(
                    {'key': key},
                    {'$set': document},
                    upsert=True
                )
                self.set_redis_cache(key, document)
                if date == today:
                    response = document
            # Store in Redis cache
            self.logger.info(f"Successfully stored flight data in MongoDB and Redis")
            return response
            
            
        except Exception as e:
            self.logger.error(f"Database operation failed: {str(e)}")
            raise

    def run_etl(self, mode: str = "arrivals", iata: str = "SIN", day: str = "1"):
        """Run the complete ETL process"""
        try:
            # Extract
            self.init_mongodb()
            self.init_redis()

            raw_data = self.extract(iata, mode, day)
            
            # Transform
            transformed_data = self.transform(raw_data, iata, mode, day)
            
            # Load
            data = self.load(transformed_data, iata, mode, day)
            
            self.logger.info("ETL process completed successfully")
            return data
        except Exception as e:
            self.logger.error(f"ETL process failed: {str(e)}")
            raise
        
    def close_connections(self):
        """Close database connections"""
        self.mongo_client.close()
        self.redis_client.close()

