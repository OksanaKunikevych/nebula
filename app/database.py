from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Optional
import logging
from .models import RawReview, ProcessedReview, ReviewMetrics

# Configure logging
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, mongodb_url: str):
        try:
            self.client = AsyncIOMotorClient(mongodb_url)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client.app_store_reviews
            self.raw_reviews = self.db.raw_reviews
            self.processed_reviews = self.db.processed_reviews
            self.metrics = self.db.metrics
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise ConnectionError(
                "Could not connect to MongoDB. Please ensure MongoDB is running locally "
                "or provide a valid MongoDB connection URL in the environment variables."
            )

    async def save_raw_reviews(self, app_id: str, app_name: str, reviews: List[dict]) -> int:
        """
        Save raw reviews to the database.
        
        Args:
            app_id: App Store ID
            app_name: Name of the app
            reviews: List of raw reviews
            
        Returns:
            Number of reviews saved
        """
        try:
            # Convert reviews to RawReview models
            raw_reviews = []
            for i, review in enumerate(reviews, 1):
                raw_review = RawReview(
                    id=i,
                    app_id=app_id,
                    app_name=app_name,
                    review_text=review.get('review', ''),
                    rating=review.get('rating', 0),
                    date_scraped=datetime.utcnow()
                )
                raw_reviews.append(raw_review.dict())
            
            # Insert reviews
            if raw_reviews:
                await self.raw_reviews.insert_many(raw_reviews)
                logger.info(f"Saved {len(raw_reviews)} raw reviews for app {app_id}")
            
            return len(raw_reviews)
        except Exception as e:
            logger.error(f"Error saving raw reviews: {str(e)}")
            raise

    async def save_processed_reviews(self, app_id: str, reviews: List[dict]) -> int:
        """
        Save processed reviews to the database.
        
        Args:
            app_id: App Store ID
            reviews: List of processed reviews
            
        Returns:
            Number of reviews saved
        """
        try:
            # Convert reviews to ProcessedReview models
            processed_reviews = []
            for i, review in enumerate(reviews, 1):
                processed_review = ProcessedReview(
                    id=i,
                    app_id=app_id,
                    cleaned_text=review.get('review_text', ''),
                    sentiment_score=review.get('sentiment_score', 0),
                    sentiment=review.get('sentiment', 'NEUTRAL'),
                    date_processed=datetime.utcnow()
                )
                processed_reviews.append(processed_review.dict())
            
            # Insert reviews
            if processed_reviews:
                await self.processed_reviews.insert_many(processed_reviews)
                logger.info(f"Saved {len(processed_reviews)} processed reviews for app {app_id}")
            
            return len(processed_reviews)
        except Exception as e:
            logger.error(f"Error saving processed reviews: {str(e)}")
            raise

    async def save_metrics(self, app_id: str, metrics: ReviewMetrics) -> None:
        """
        Save or update metrics for an app.
        
        Args:
            app_id: App Store ID
            metrics: ReviewMetrics object containing metrics data
        """
        try:
            # Convert ReviewMetrics to dict and add app_id
            metrics_data = metrics.dict()
            metrics_data["app_id"] = app_id
            
            # Update or insert metrics
            await self.metrics.update_one(
                {"app_id": app_id},
                {"$set": metrics_data},
                upsert=True
            )
            logger.info(f"Saved metrics for app {app_id}")
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")
            raise

    async def get_raw_reviews(self, app_id: str, limit: int = 100) -> List[dict]:
        """
        Get raw reviews for an app.
        
        Args:
            app_id: App Store ID
            limit: Maximum number of reviews to return
            
        Returns:
            List of raw reviews
        """
        try:
            cursor = self.raw_reviews.find({"app_id": app_id}).limit(limit)
            reviews = await cursor.to_list(length=limit)
            return reviews
        except Exception as e:
            logger.error(f"Error getting raw reviews: {str(e)}")
            raise

    async def get_processed_reviews(self, app_id: str, limit: int = 100) -> List[dict]:
        """
        Get processed reviews for an app.
        
        Args:
            app_id: App Store ID
            limit: Maximum number of reviews to return
            
        Returns:
            List of processed reviews
        """
        try:
            cursor = self.processed_reviews.find({"app_id": app_id}).limit(limit)
            reviews = await cursor.to_list(length=limit)
            return reviews
        except Exception as e:
            logger.error(f"Error getting processed reviews: {str(e)}")
            raise

    async def get_metrics(self, app_id: str) -> Optional[dict]:
        """
        Get metrics for an app.
        
        Args:
            app_id: App Store ID
            
        Returns:
            Dictionary containing metrics data
        """
        try:
            metrics = await self.metrics.find_one({"app_id": app_id})
            return metrics
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            raise 