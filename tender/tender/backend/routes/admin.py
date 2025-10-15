# routes/admin.py - FIXED ADMIN ROUTES
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, mongo_db, convert_mongo_cursor, convert_mongo_doc
from admin_panel import admin_service
from auth import get_current_user, require_team_admin
from schemas import SuccessResponse, UserResponse
from ocds_client import OCDSClient
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])
ocds_client = OCDSClient()

@router.get("/stats")
async def get_admin_stats(
    current_user: UserResponse = Depends(require_team_admin),
    db: Session = Depends(get_db)
):
    """Get system statistics"""
    try:
        stats = admin_service.get_system_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Error getting admin stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity")
async def get_admin_activity(
    current_user: UserResponse = Depends(require_team_admin),
    limit: int = 20
):
    """Get user activity - FIXED VERSION"""
    try:
        # Get SQL activity from admin service
        sql_activities = admin_service.get_user_activity(days=7)
        
        # Get MongoDB activity logs
        mongo_activities = []
        try:
            # Use the helper function to properly serialize MongoDB data
            mongo_cursor = mongo_db.activity_logs.find().sort("timestamp", -1).limit(limit)
            mongo_activities = convert_mongo_cursor(mongo_cursor)
        except Exception as mongo_error:
            logger.warning(f"Could not fetch MongoDB activities: {mongo_error}")
        
        # Combine and sort activities
        all_activities = sql_activities + mongo_activities
        
        # Sort by timestamp (handle different field names)
        def get_timestamp(activity):
            if 'timestamp' in activity:
                return activity['timestamp']
            elif 'created_at' in activity:
                return activity['created_at']
            elif 'last_updated_at' in activity:
                return activity['last_updated_at']
            else:
                return None
        
        # Filter out None timestamps and sort
        valid_activities = [a for a in all_activities if get_timestamp(a) is not None]
        valid_activities.sort(key=get_timestamp, reverse=True)
        
        return {
            "success": True, 
            "data": valid_activities[:limit]  # Limit to requested number
        }
        
    except Exception as e:
        logger.error(f"Error getting admin activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/tenders")
async def get_tender_analytics(
    current_user: UserResponse = Depends(require_team_admin),
    db: Session = Depends(get_db)
):
    """Get tender analytics"""
    try:
        analytics = admin_service.get_tender_analytics()
        return {"success": True, "data": analytics}
    except Exception as e:
        logger.error(f"Error getting tender analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/teams")
async def get_team_analytics(
    current_user: UserResponse = Depends(require_team_admin),
    db: Session = Depends(get_db)
):
    """Get team analytics"""
    try:
        analytics = admin_service.get_team_analytics()
        return {"success": True, "data": analytics}
    except Exception as e:
        logger.error(f"Error getting team analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-tenders")
async def sync_tenders(
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(require_team_admin),
    limit: int = 50
):
    """Admin endpoint: Sync tenders from OCDS API"""
    def sync_task():
        try:
            stats = ocds_client.sync_tenders_to_database(limit)
            print(f"✅ Tender sync completed: {stats}")
        except Exception as e:
            print(f"❌ Tender sync failed: {e}")
    
    background_tasks.add_task(sync_task)
    
    return SuccessResponse(
        message="Tender sync started in background",
        data={"limit": limit}
    )

@router.post("/cleanup")
async def cleanup_old_data(
    days_old: int = 90,
    current_user: UserResponse = Depends(require_team_admin),
    db: Session = Depends(get_db)
):
    """Clean up old data"""
    try:
        result = admin_service.cleanup_old_data(days_old)
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Error cleaning up data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mongo-stats")
async def get_mongo_stats(current_user: UserResponse = Depends(require_team_admin)):
    """Get MongoDB statistics"""
    try:
        # Get counts from MongoDB collections
        ai_summaries_count = mongo_db.ai_summaries.count_documents({})
        readiness_scores_count = mongo_db.readiness_scores.count_documents({})
        activity_logs_count = mongo_db.activity_logs.count_documents({})
        
        # Get recent activity from MongoDB
        recent_activity = convert_mongo_cursor(
            mongo_db.activity_logs.find()
            .sort("timestamp", -1)
            .limit(10)
        )
        
        return {
            "success": True,
            "data": {
                "ai_summaries": ai_summaries_count,
                "readiness_scores": readiness_scores_count,
                "activity_logs": activity_logs_count,
                "recent_activity": recent_activity
            }
        }
    except Exception as e:
        logger.error(f"Error getting MongoDB stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))