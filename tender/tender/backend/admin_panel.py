# admin_panel.py - FIXED VERSION
from database import SessionLocal, User, Team, Tender, CompanyProfile, WorkspaceTender
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self):
        self.db = SessionLocal()
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            # Basic counts
            total_users = self.db.query(User).count()
            total_teams = self.db.query(Team).count()
            total_tenders = self.db.query(Tender).count()
            total_profiles = self.db.query(CompanyProfile).count()
            total_workspace = self.db.query(WorkspaceTender).count()
            
            # Plan distribution
            plan_stats = self.db.query(
                Team.plan_tier,
                self.db.func.count(Team.id).label('count')
            ).group_by(Team.plan_tier).all()
            
            # Recent activity (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_users = self.db.query(User).filter(User.created_at >= week_ago).count()
            recent_tenders = self.db.query(Tender).filter(Tender.created_at >= week_ago).count()
            
            # User activity stats
            active_teams = self.db.query(WorkspaceTender.team_id).distinct().count()
            
            return {
                "users": total_users,
                "teams": total_teams,
                "tenders": total_tenders,
                "profiles": total_profiles,
                "workspace_entries": total_workspace,
                "plan_distribution": {stat.plan_tier: stat.count for stat in plan_stats},
                "recent_users": recent_users,
                "recent_tenders": recent_tenders,
                "active_teams": active_teams,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {
                "error": str(e),
                "users": 0,
                "teams": 0,
                "tenders": 0,
                "profiles": 0,
                "workspace_entries": 0,
                "plan_distribution": {},
                "recent_users": 0,
                "recent_tenders": 0,
                "active_teams": 0,
                "last_updated": datetime.utcnow().isoformat()
            }
        finally:
            self.db.close()
    
    def get_user_activity(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent user activity"""
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Get recent users and their activities
            recent_users = self.db.query(User).filter(
                User.created_at >= since_date
            ).order_by(User.created_at.desc()).limit(50).all()
            
            activities = []
            for user in recent_users:
                team = self.db.query(Team).filter(Team.id == user.team_id).first()
                team_name = team.name if team else "Unknown Team"
                
                activities.append({
                    "timestamp": user.created_at,
                    "user_name": user.full_name,
                    "user_email": user.email,
                    "action": "Registered",
                    "details": {
                        "team": team_name,
                        "user_id": user.id
                    }
                })
            
            # Get recent workspace activities
            recent_workspace = self.db.query(WorkspaceTender).filter(
                WorkspaceTender.last_updated_at >= since_date
            ).order_by(WorkspaceTender.last_updated_at.desc()).limit(20).all()
            
            for ws in recent_workspace:
                user = self.db.query(User).filter(User.id == ws.last_updated_by).first()
                tender = self.db.query(Tender).filter(Tender.id == ws.tender_id).first()
                
                if user and tender:
                    activities.append({
                        "timestamp": ws.last_updated_at,
                        "user_name": user.full_name,
                        "user_email": user.email,
                        "action": f"Updated tender workspace status to '{ws.status}'",
                        "details": {
                            "tender_title": tender.title,
                            "tender_id": tender.tender_id,
                            "workspace_id": ws.id
                        }
                    })
            
            # Sort all activities by timestamp
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            return activities[:50]
            
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return []
        finally:
            self.db.close()
    
    def get_tender_analytics(self) -> Dict[str, Any]:
        """Get tender analytics - FIXED VERSION (no status field)"""
        try:
            # Tenders by province
            province_stats = self.db.query(
                Tender.province,
                self.db.func.count(Tender.id).label('count')
            ).group_by(Tender.province).all()
            
            # Tenders by buyer
            buyer_stats = self.db.query(
                Tender.buyer_organization,
                self.db.func.count(Tender.id).label('count')
            ).group_by(Tender.buyer_organization).order_by(
                self.db.func.count(Tender.id).desc()
            ).limit(10).all()
            
            # Upcoming deadlines (next 30 days)
            upcoming_deadline = datetime.utcnow() + timedelta(days=30)
            upcoming_tenders = self.db.query(Tender).filter(
                Tender.submission_deadline <= upcoming_deadline,
                Tender.submission_deadline >= datetime.utcnow()
            ).count()
            
            # FIXED: Removed status stats since Tender model doesn't have status field
            # Instead, add budget analysis
            tenders_with_budget = self.db.query(Tender).filter(
                Tender.budget_min.isnot(None)
            ).count()
            
            return {
                "by_province": {stat.province: stat.count for stat in province_stats if stat.province},
                "top_buyers": {stat.buyer_organization: stat.count for stat in buyer_stats if stat.buyer_organization},
                "upcoming_tenders": upcoming_tenders,
                "total_buyers": len(buyer_stats),
                "tenders_with_budget": tenders_with_budget,
                "total_tenders": self.db.query(Tender).count()
            }
            
        except Exception as e:
            logger.error(f"Error getting tender analytics: {e}")
            return {
                "by_province": {},
                "top_buyers": {},
                "upcoming_tenders": 0,
                "total_buyers": 0,
                "tenders_with_budget": 0,
                "total_tenders": 0
            }
        finally:
            self.db.close()
    
    def get_team_analytics(self) -> Dict[str, Any]:
        """Get team analytics"""
        try:
            # Teams by plan tier
            teams_by_plan = self.db.query(
                Team.plan_tier,
                self.db.func.count(Team.id).label('count')
            ).group_by(Team.plan_tier).all()
            
            # Teams with active workspace entries
            active_teams = self.db.query(WorkspaceTender.team_id).distinct().count()
            total_teams = self.db.query(Team).count()
            
            return {
                "teams_by_plan": {team.plan_tier: team.count for team in teams_by_plan},
                "active_teams": active_teams,
                "total_teams": total_teams,
                "inactive_teams": total_teams - active_teams
            }
            
        except Exception as e:
            logger.error(f"Error getting team analytics: {e}")
            return {}
        finally:
            self.db.close()
    
    def cleanup_old_data(self, days_old: int = 90):
        """Clean up old data"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Clean old tenders (keep sample data)
            old_tenders = self.db.query(Tender).filter(
                Tender.created_at < cutoff_date,
                ~Tender.tender_id.like('TENDER-%')  # Keep sample tenders
            ).delete()
            
            self.db.commit()
            
            return {
                "old_tenders_deleted": old_tenders,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cleaning old data: {e}")
            return {"old_tenders_deleted": 0, "error": str(e)}
        finally:
            self.db.close()

# Global instance
admin_service = AdminService()