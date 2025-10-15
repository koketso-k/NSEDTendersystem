# mongodb_service.py - COMPLETELY FIXED VERSION

from pymongo import MongoClient, DESCENDING, ASCENDING
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Optional
from bson import ObjectId
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self):
        """Initialize MongoDB connection with proper configuration"""
        try:
            self.client = MongoClient(
                os.getenv("MONGO_URL", "mongodb://localhost:27017/"),
                serverSelectionTimeoutMS=10000,  # Increased timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=30000,
                maxPoolSize=50,
                waitQueueTimeoutMS=10000
            )
            
            # Test connection with longer timeout
            self.client.admin.command('ping', maxTimeMS=5000)
            self.db = self.client["tender_hub"]  # Fixed database name to match your setup
            
            # Initialize collections with validation (if needed)
            # REMOVED: self._ensure_indexes() - Indexes are created in database.py
            logger.info("✅ MongoDB connected successfully")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            # Don't raise, create a null client for graceful degradation
            self.client = None
            self.db = None

    def _ensure_indexes(self):
        """Create necessary indexes for performance - FIXED: Check if indexes exist first"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            logger.warning("❌ MongoDB database not available for index creation")
            return
            
        try:
            # Check existing indexes to avoid conflicts
            existing_indexes = {}
            for collection_name in ["ai_summaries", "readiness_scores", "activity_logs", "analytics_cache", "user_searches"]:
                if collection_name in self.db.list_collection_names():
                    existing_indexes[collection_name] = [idx["name"] for idx in self.db[collection_name].list_indexes()]
                else:
                    existing_indexes[collection_name] = []

            # AI Summaries collection - only create if they don't exist
            if "tender_id_1" not in existing_indexes.get("ai_summaries", []):
                self.db.ai_summaries.create_index([("tender_id", ASCENDING)], unique=True, name="tender_id_1")
            if "team_id_1" not in existing_indexes.get("ai_summaries", []):
                self.db.ai_summaries.create_index([("team_id", ASCENDING)], name="team_id_1")
            if "generated_at_-1" not in existing_indexes.get("ai_summaries", []):
                self.db.ai_summaries.create_index([("generated_at", DESCENDING)], name="generated_at_-1")
            
            # Readiness Scores collection - FIXED: Use consistent index names
            readiness_index_name = "team_id_1_calculated_at_-1"
            if readiness_index_name not in existing_indexes.get("readiness_scores", []):
                self.db.readiness_scores.create_index(
                    [("team_id", ASCENDING), ("calculated_at", DESCENDING)], 
                    name=readiness_index_name
                )
            if "tender_id_1" not in existing_indexes.get("readiness_scores", []):
                self.db.readiness_scores.create_index([("tender_id", ASCENDING)], name="tender_id_1")
            if "company_profile_id_1" not in existing_indexes.get("readiness_scores", []):
                self.db.readiness_scores.create_index([("company_profile_id", ASCENDING)], name="company_profile_id_1")
            
            # Activity Logs collection - FIXED: Removed TTL index that was deleting logs
            if "user_id_1_timestamp_-1" not in existing_indexes.get("activity_logs", []):
                self.db.activity_logs.create_index(
                    [("user_id", ASCENDING), ("timestamp", DESCENDING)], 
                    name="user_id_1_timestamp_-1"
                )
            if "team_id_1_timestamp_-1" not in existing_indexes.get("activity_logs", []):
                self.db.activity_logs.create_index(
                    [("team_id", ASCENDING), ("timestamp", DESCENDING)], 
                    name="team_id_1_timestamp_-1"
                )
            if "action_1" not in existing_indexes.get("activity_logs", []):
                self.db.activity_logs.create_index([("action", ASCENDING)], name="action_1")
            
            # Analytics Cache collection
            if "analytics_type_1" not in existing_indexes.get("analytics_cache", []):
                self.db.analytics_cache.create_index([("analytics_type", ASCENDING)], unique=True, name="analytics_type_1")
            if "expires_at_1" not in existing_indexes.get("analytics_cache", []):
                self.db.analytics_cache.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0, name="expires_at_1")
            
            # User Searches collection (for rate limiting)
            if "user_id_1_search_date_-1" not in existing_indexes.get("user_searches", []):
                self.db.user_searches.create_index(
                    [("user_id", ASCENDING), ("search_date", DESCENDING)], 
                    name="user_id_1_search_date_-1"
                )
            if "search_date_1" not in existing_indexes.get("user_searches", []):
                self.db.user_searches.create_index([("search_date", ASCENDING)], expireAfterSeconds=7*24*60*60, name="search_date_1")
            
            logger.info("✅ MongoDB indexes verified/created successfully")
            
        except Exception as e:
            logger.error(f"⚠️ Error creating indexes: {e}")

    # ========== AI SUMMARIES ==========

    def store_ai_summary(self, tender_id: int, document_url: str, summary: str, 
                        key_points: Dict[str, Any], user_id: int, team_id: int) -> bool:
        """Store AI-generated summary in MongoDB"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            logger.warning("❌ MongoDB not available for storing AI summary")
            return False
            
        try:
            summary_doc = {
                "tender_id": tender_id,
                "document_url": document_url,
                "summary": summary,
                "key_points": key_points,
                "generated_at": datetime.utcnow(),
                "generated_by": user_id,
                "team_id": team_id,
                "version": "1.0"
            }
            
            # Upsert to handle updates
            result = self.db.ai_summaries.update_one(
                {"tender_id": tender_id},
                {"$set": summary_doc},
                upsert=True
            )
            
            logger.info(f"✅ AI summary stored/updated for tender {tender_id}")
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"❌ Error storing AI summary: {e}")
            return False

    def get_tender_summary(self, tender_id: int) -> Optional[Dict[str, Any]]:
        """Get AI summary for a tender"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return None
            
        try:
            doc = self.db.ai_summaries.find_one({"tender_id": tender_id})
            return self._convert_objectid_to_str(doc) if doc else None
        except Exception as e:
            logger.error(f"❌ Error getting tender summary: {e}")
            return None

    def get_team_summaries(self, team_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent AI summaries for a team"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return []
            
        try:
            docs = list(self.db.ai_summaries.find(
                {"team_id": team_id}
            ).sort("generated_at", DESCENDING).limit(limit))
            return [self._convert_objectid_to_str(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ Error getting team summaries: {e}")
            return []

    # ========== READINESS SCORES ==========

    def store_readiness_score(self, tender_id: int, company_profile_id: int, 
                            team_id: int, score_data: Dict[str, Any], user_id: int) -> bool:
        """Store readiness scoring results in MongoDB"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            logger.warning("❌ MongoDB not available for storing readiness score")
            return False
            
        try:
            score_doc = {
                "tender_id": tender_id,
                "company_profile_id": company_profile_id,
                "team_id": team_id,
                "suitability_score": score_data.get("suitability_score", 0),
                "checklist": score_data.get("checklist", {}),
                "recommendation": score_data.get("recommendation", ""),
                "scoring_breakdown": score_data.get("scoring_breakdown", {}),
                "tender_requirements": score_data.get("tender_requirements", {}),
                "calculated_at": datetime.utcnow(),
                "calculated_by": user_id
            }
            
            result = self.db.readiness_scores.insert_one(score_doc)
            logger.info(f"✅ Readiness score stored for tender {tender_id}")
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"❌ Error storing readiness score: {e}")
            return False

    def get_readiness_history(self, company_profile_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get readiness score history for a company"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return []
            
        try:
            docs = list(self.db.readiness_scores.find(
                {"company_profile_id": company_profile_id}
            ).sort("calculated_at", DESCENDING).limit(limit))
            return [self._convert_objectid_to_str(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ Error getting readiness history: {e}")
            return []

    def get_team_readiness_scores(self, team_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent readiness scores for a team"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return []
            
        try:
            docs = list(self.db.readiness_scores.find(
                {"team_id": team_id}
            ).sort("calculated_at", DESCENDING).limit(limit))
            return [self._convert_objectid_to_str(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ Error getting team readiness scores: {e}")
            return []

    # ========== ACTIVITY LOGS - FIXED VERSION ==========

    def log_user_activity(self, user_id: int, team_id: int, action: str, details: Dict[str, Any] = None) -> bool:
        """Log user activity in MongoDB - FIXED with proper write concern"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            logger.warning("❌ MongoDB not available for activity logging")
            return False
            
        try:
            log_entry = {
                "user_id": user_id,
                "team_id": team_id,
                "action": action,
                "details": details or {},
                "timestamp": datetime.utcnow(),
                "ip_address": "0.0.0.0"  # Would be populated from request in production
            }
            
            # Use write concern for immediate acknowledgement
            result = self.db.activity_logs.insert_one(log_entry)
            
            if result.acknowledged:
                logger.info(f"✅ User activity logged: {action} (ID: {result.inserted_id})")
                return True
            else:
                logger.warning(f"⚠️ Activity log not acknowledged: {action}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error logging user activity: {e}")
            return False

    def get_user_activity(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user activity history"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return []
            
        try:
            docs = list(self.db.activity_logs.find(
                {"user_id": user_id}
            ).sort("timestamp", DESCENDING).limit(limit))
            return [self._convert_objectid_to_str(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ Error getting user activity: {e}")
            return []

    def get_team_activity(self, team_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get team activity history"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return []
            
        try:
            docs = list(self.db.activity_logs.find(
                {"team_id": team_id}
            ).sort("timestamp", DESCENDING).limit(limit))
            return [self._convert_objectid_to_str(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ Error getting team activity: {e}")
            return []

    def get_all_activity_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all activity logs for debugging"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return []
            
        try:
            docs = list(self.db.activity_logs.find()
                       .sort("timestamp", DESCENDING)
                       .limit(limit))
            return [self._convert_objectid_to_str(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ Error getting all activity logs: {e}")
            return []

    def get_recent_searches(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent searches for a user (for rate limiting)"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return []
            
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            docs = list(self.db.activity_logs.find({
                "user_id": user_id,
                "action": "tender_search",
                "timestamp": {"$gte": cutoff_date}
            }))
            return [self._convert_objectid_to_str(doc) for doc in docs]
        except Exception as e:
            logger.error(f"❌ Error getting recent searches: {e}")
            return []

    # ========== ANALYTICS CACHE ==========

    def cache_analytics(self, analytics_type: str, data: Dict[str, Any], expiry_hours: int = 24) -> bool:
        """Cache analytics data in MongoDB with TTL"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return False
            
        try:
            cache_doc = {
                "analytics_type": analytics_type,
                "data": data,
                "cached_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=expiry_hours)
            }
            
            # Remove old cache for this analytics type
            self.db.analytics_cache.delete_many({"analytics_type": analytics_type})
            result = self.db.analytics_cache.insert_one(cache_doc)
            
            logger.info(f"✅ Analytics cached: {analytics_type}")
            return result.acknowledged
            
        except Exception as e:
            logger.error(f"❌ Error caching analytics: {e}")
            return False

    def get_cached_analytics(self, analytics_type: str) -> Optional[Dict[str, Any]]:
        """Get cached analytics data"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return None
            
        try:
            cache_doc = self.db.analytics_cache.find_one({"analytics_type": analytics_type})
            if cache_doc and cache_doc.get("expires_at", datetime.utcnow()) > datetime.utcnow():
                return cache_doc.get("data")
            else:
                # Remove expired cache
                self.db.analytics_cache.delete_many({"analytics_type": analytics_type})
                return None
        except Exception as e:
            logger.error(f"❌ Error getting cached analytics: {e}")
            return None

    # ========== DATABASE MANAGEMENT ==========

    def cleanup_old_data(self, days_old: int = 90) -> Dict[str, int]:
        """Clean up old data from MongoDB (admin function)"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return {"activity_logs_deleted": 0, "analytics_cache_deleted": 0}
            
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Clean old activity logs (keep recent ones only)
            activity_result = self.db.activity_logs.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            # Clean old analytics cache (expired ones are auto-deleted by TTL index)
            analytics_result = self.db.analytics_cache.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            logger.info(f"✅ Cleaned up {activity_result.deleted_count} old activity logs")
            logger.info(f"✅ Cleaned up {analytics_result.deleted_count} expired analytics caches")
            
            return {
                "activity_logs_deleted": activity_result.deleted_count,
                "analytics_cache_deleted": analytics_result.deleted_count
            }
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {e}")
            return {"activity_logs_deleted": 0, "analytics_cache_deleted": 0}

    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about MongoDB collections"""
        # FIXED: Use explicit None check instead of truthiness
        if self.db is None:
            return {"error": "MongoDB not available"}
            
        try:
            stats = {
                "ai_summaries": self.db.ai_summaries.count_documents({}),
                "readiness_scores": self.db.readiness_scores.count_documents({}),
                "activity_logs": self.db.activity_logs.count_documents({}),
                "analytics_cache": self.db.analytics_cache.count_documents({}),
                "user_searches": self.db.user_searches.count_documents({}) if 'user_searches' in self.db.list_collection_names() else 0,
                "collections": list(self.db.list_collection_names()),
                "timestamp": datetime.utcnow().isoformat()
            }
            return stats
        except Exception as e:
            logger.error(f"❌ Error getting database stats: {e}")
            return {"error": str(e)}

    # ========== HELPER METHODS ==========

    def _convert_objectid_to_str(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectId to string for JSON serialization"""
        if doc and '_id' in doc and isinstance(doc['_id'], ObjectId):
            doc['_id'] = str(doc['_id'])
        return doc

    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        # FIXED: Use explicit None checks
        return self.client is not None and self.db is not None

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client is not None:
            try:
                self.client.close()
                self.client = None
                self.db = None
                logger.info("✅ MongoDB connection closed")
            except Exception as e:
                logger.error(f"❌ Error closing MongoDB connection: {e}")

# Global instance for easy import
mongodb_service = MongoDBService()