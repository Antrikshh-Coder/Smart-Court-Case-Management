"""
Judge resolver for Smart Court Case Management System
Handles all judge-related queries and mutations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from strawberry import field
import strawberry
from db import get_db, Judge as JudgeModel, Hearing, Case
from app.types import Judge, JudgeInput, JudgeResponse, Case as CaseType
from app.utils import (
    validate_judge_exists,
    format_error_message,
    format_success_message
)


# Query Resolvers
@strawberry.type
class JudgeQuery:
    """Query resolver for judges"""
    
    @field
    def get_judges(self, info: strawberry.Info) -> List[Judge]:
        """
        Get all judges
        
        Returns:
            List[Judge]: List of all judges
        """
        db = next(get_db())
        try:
            judges = db.query(JudgeModel).all()
            return judges
        finally:
            db.close()
    
    @field
    def get_judge_by_id(self, info: strawberry.Info, judge_id: int) -> Optional[Judge]:
        """
        Get a judge by ID
        
        Args:
            judge_id: ID of the judge to retrieve
        
        Returns:
            Optional[Judge]: Judge if found, None otherwise
        """
        db = next(get_db())
        try:
            judge = db.query(JudgeModel).filter(JudgeModel.id == judge_id).first()
            return judge
        finally:
            db.close()
    
    @field
    def get_judge_cases(self, info: strawberry.Info, judge_id: int) -> List[CaseType]:
        """
        Get all cases assigned to a judge
        
        Args:
            judge_id: ID of the judge
        
        Returns:
            List[Case]: List of cases assigned to the judge
        """
        db = next(get_db())
        try:
            # Validate judge exists
            judge = db.query(JudgeModel).filter(JudgeModel.id == judge_id).first()
            if not judge:
                return []
            
            # Get all hearings for this judge
            hearings = db.query(Hearing).filter(Hearing.judge_id == judge_id).all()
            
            # Get unique cases from these hearings
            case_ids = list(set([hearing.case_id for hearing in hearings]))
            cases = db.query(Case).filter(Case.id.in_(case_ids)).all()
            
            return cases
        finally:
            db.close()
    
    @field
    def get_judges_by_court_room(self, info: strawberry.Info, court_room: str) -> List[Judge]:
        """
        Get judges by court room
        
        Args:
            court_room: Court room to filter judges by
        
        Returns:
            List[Judge]: List of judges in the specified court room
        """
        db = next(get_db())
        try:
            judges = db.query(JudgeModel).filter(JudgeModel.court_room == court_room).all()
            return judges
        finally:
            db.close()


# Mutation Resolvers
@strawberry.type
class JudgeMutation:
    """Mutation resolver for judges"""
    
    @field
    def create_judge(self, info: strawberry.Info, input: JudgeInput) -> JudgeResponse:
        """
        Create a new judge
        
        Args:
            input: Judge input data
        
        Returns:
            JudgeResponse: Response with created judge or error
        """
        db = next(get_db())
        try:
            # Check if judge with same name and court room already exists
            existing_judge = db.query(JudgeModel).filter(
                JudgeModel.name == input.name,
                JudgeModel.court_room == input.court_room
            ).first()
            
            if existing_judge:
                return JudgeResponse(
                    success=False,
                    message=format_error_message("create judge", "Judge with this name and court room already exists")
                )
            
            # Create new judge
            new_judge = JudgeModel(
                name=input.name,
                court_room=input.court_room
            )
            
            db.add(new_judge)
            db.commit()
            db.refresh(new_judge)
            
            return JudgeResponse(
                success=True,
                message=format_success_message("created", "judge"),
                judge=new_judge
            )
            
        except Exception as e:
            db.rollback()
            return JudgeResponse(
                success=False,
                message=format_error_message("create judge", str(e))
            )
        finally:
            db.close()
    
    @field
    def update_judge(self, info: strawberry.Info, judge_id: int, name: Optional[str] = None, court_room: Optional[str] = None) -> JudgeResponse:
        """
        Update judge information
        
        Args:
            judge_id: ID of the judge to update
            name: New name (optional)
            court_room: New court room (optional)
        
        Returns:
            JudgeResponse: Response with updated judge or error
        """
        db = next(get_db())
        try:
            # Get the judge
            judge = db.query(JudgeModel).filter(JudgeModel.id == judge_id).first()
            if not judge:
                return JudgeResponse(
                    success=False,
                    message=format_error_message("update judge", "Judge not found")
                )
            
            # Update fields if provided
            if name:
                judge.name = name
            if court_room:
                judge.court_room = court_room
            
            db.commit()
            db.refresh(judge)
            
            return JudgeResponse(
                success=True,
                message=format_success_message("updated", "judge"),
                judge=judge
            )
            
        except Exception as e:
            db.rollback()
            return JudgeResponse(
                success=False,
                message=format_error_message("update judge", str(e))
            )
        finally:
            db.close()
    
    @field
    def delete_judge(self, info: strawberry.Info, judge_id: int) -> JudgeResponse:
        """
        Delete a judge (only if no hearings are assigned)
        
        Args:
            judge_id: ID of the judge to delete
        
        Returns:
            JudgeResponse: Response with deletion status
        """
        db = next(get_db())
        try:
            # Get the judge
            judge = db.query(JudgeModel).filter(JudgeModel.id == judge_id).first()
            if not judge:
                return JudgeResponse(
                    success=False,
                    message=format_error_message("delete judge", "Judge not found")
                )
            
            # Check if judge has any hearings
            hearing_count = db.query(Hearing).filter(Hearing.judge_id == judge_id).count()
            if hearing_count > 0:
                return JudgeResponse(
                    success=False,
                    message=format_error_message("delete judge", f"Judge has {hearing_count} hearings assigned")
                )
            
            # Delete the judge
            db.delete(judge)
            db.commit()
            
            return JudgeResponse(
                success=True,
                message=format_success_message("deleted", "judge"),
                judge=judge
            )
            
        except Exception as e:
            db.rollback()
            return JudgeResponse(
                success=False,
                message=format_error_message("delete judge", str(e))
            )
        finally:
            db.close()
