from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Optional
import logging
from bson import ObjectId
from .models import RawReview, ProcessedReview, ReviewMetrics
from .nlp_analysis import InsightAnalysis

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
            self.insights = self.db.insights
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise ConnectionError(
                "Could not connect to MongoDB. Please ensure MongoDB is running locally "
                "or provide a valid MongoDB connection URL in the environment variables."
            )

    def _convert_to_dict(self, data: dict) -> dict:
        """Convert MongoDB document to JSON-serializable dictionary."""
        if not data:
            return {}
        
        # Convert ObjectId to string
        if '_id' in data:
            data['_id'] = str(data['_id'])
        
        # Convert datetime to ISO format string
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, ObjectId):
                data[key] = str(value)
        
        return data

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
            for review in reviews:
                raw_review = RawReview(
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
            for review in reviews:
                processed_review = ProcessedReview(
                    app_id=app_id,
                    review_text=review.get('review_text', ''),
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

    async def save_insights(self, app_id: str, insights: InsightAnalysis) -> None:
        """
        Save or update insights for an app.
        
        Args:
            app_id: App Store ID
            insights: InsightAnalysis object containing NLP insights
        """
        try:
            # Convert InsightAnalysis to dict and add app_id
            insights_data = insights.dict()
            insights_data["app_id"] = app_id
            insights_data["last_updated"] = datetime.utcnow()
            
            # Update or insert insights
            await self.insights.update_one(
                {"app_id": app_id},
                {"$set": insights_data},
                upsert=True
            )
            logger.info(f"Saved insights for app {app_id}")
        except Exception as e:
            logger.error(f"Error saving insights: {str(e)}")
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
            return [self._convert_to_dict(review) for review in reviews]
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
            return [self._convert_to_dict(review) for review in reviews]
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
            return self._convert_to_dict(metrics)
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            raise

    async def get_insights(self, app_id: str) -> Optional[dict]:
        """
        Get insights for an app.
        
        Args:
            app_id: App Store ID
            
        Returns:
            Dictionary containing insights data
        """
        try:
            insights = await self.insights.find_one({"app_id": app_id})
            return self._convert_to_dict(insights)
        except Exception as e:
            logger.error(f"Error getting insights: {str(e)}")
            raise 