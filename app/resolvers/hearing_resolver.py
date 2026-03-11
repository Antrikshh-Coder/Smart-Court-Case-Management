"""
Hearing resolver for Smart Court Case Management System
Handles all hearing-related queries and mutations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from strawberry import field
import strawberry

from db import get_db, Hearing as HearingModel, Case, Judge, HearingStatusEnum, CaseStatusEnum
from app.types import Hearing, HearingInput, HearingResponse, HearingStatus, Case as CaseType
from app.utils import (
    check_hearing_overlap,
    validate_case_exists,
    validate_judge_exists,
    validate_hearing_exists,
    validate_date_not_in_past,
    format_error_message,
    format_success_message
)


# Query Resolvers
@strawberry.type
class HearingQuery:
    """Query resolver for hearings"""
    
    @field
    def get_hearings(self, info: strawberry.Info) -> List[Hearing]:
        """
        Get all hearings
        
        Returns:
            List[Hearing]: List of all hearings
        """
        db = next(get_db())
        try:
            hearings = db.query(HearingModel).all()
            return hearings
        finally:
            db.close()
    
    @field
    def get_hearing_by_id(self, info: strawberry.Info, hearing_id: int) -> Optional[Hearing]:
        """
        Get a hearing by ID
        
        Args:
            hearing_id: ID of the hearing to retrieve
        
        Returns:
            Optional[Hearing]: Hearing if found, None otherwise
        """
        db = next(get_db())
        try:
            hearing = db.query(HearingModel).filter(HearingModel.id == hearing_id).first()
            return hearing
        finally:
            db.close()
    
    @field
    def get_hearings_by_case(self, info: strawberry.Info, case_id: int) -> List[Hearing]:
        """
        Get all hearings for a specific case
        
        Args:
            case_id: ID of the case
        
        Returns:
            List[Hearing]: List of hearings for the case
        """
        db = next(get_db())
        try:
            # Validate case exists
            case_exists, error_msg = validate_case_exists(db, case_id)
            if not case_exists:
                return []
            
            hearings = db.query(HearingModel).filter(HearingModel.case_id == case_id).all()
            return hearings
        finally:
            db.close()
    
    @field
    def get_hearings_by_judge(self, info: strawberry.Info, judge_id: int) -> List[Hearing]:
        """
        Get all hearings for a specific judge
        
        Args:
            judge_id: ID of the judge
        
        Returns:
            List[Hearing]: List of hearings for the judge
        """
        db = next(get_db())
        try:
            # Validate judge exists
            judge_exists, error_msg = validate_judge_exists(db, judge_id)
            if not judge_exists:
                return []
            
            hearings = db.query(HearingModel).filter(HearingModel.judge_id == judge_id).all()
            return hearings
        finally:
            db.close()
    
    @field
    def get_scheduled_hearings(self, info: strawberry.Info) -> List[Hearing]:
        """
        Get all scheduled hearings (not completed)
        
        Returns:
            List[Hearing]: List of scheduled hearings
        """
        db = next(get_db())
        try:
            hearings = db.query(HearingModel).filter(HearingModel.status == HearingStatusEnum.SCHEDULED).all()
            return hearings
        finally:
            db.close()
    
    @field
    def get_hearings_by_date(self, info: strawberry.Info, hearing_date: str) -> List[Hearing]:
        """
        Get hearings by date
        
        Args:
            hearing_date: Date in YYYY-MM-DD format
        
        Returns:
            List[Hearing]: List of hearings on the specified date
        """
        from datetime import datetime
        
        try:
            date_obj = datetime.strptime(hearing_date, "%Y-%m-%d").date()
        except ValueError:
            return []
        
        db = next(get_db())
        try:
            hearings = db.query(HearingModel).filter(HearingModel.hearing_date == date_obj).all()
            return hearings
        finally:
            db.close()


# Mutation Resolvers
@strawberry.type
class HearingMutation:
    """Mutation resolver for hearings"""
    
    @field
    def schedule_hearing(self, info: strawberry.Info, input: HearingInput) -> HearingResponse:
        """
        Schedule a new hearing
        
        Args:
            input: Hearing input data
        
        Returns:
            HearingResponse: Response with created hearing or error
        """
        db = next(get_db())
        try:
            # Validate case exists
            case_exists, case_error = validate_case_exists(db, input.case_id)
            if not case_exists:
                return HearingResponse(
                    success=False,
                    message=format_error_message("schedule hearing", case_error)
                )
            
            # Validate judge exists
            judge_exists, judge_error = validate_judge_exists(db, input.judge_id)
            if not judge_exists:
                return HearingResponse(
                    success=False,
                    message=format_error_message("schedule hearing", judge_error)
                )
            
            # Validate date is not in past
            date_valid, date_error = validate_date_not_in_past(input.hearing_date)
            if not date_valid:
                return HearingResponse(
                    success=False,
                    message=format_error_message("schedule hearing", date_error)
                )
            
            # Check for overlapping hearings for the same judge
            if check_hearing_overlap(db, input.judge_id, input.hearing_date):
                return HearingResponse(
                    success=False,
                    message=format_error_message(
                        "schedule hearing", 
                        "Judge already has a hearing scheduled on this date"
                    )
                )
            
            # Create new hearing
            new_hearing = HearingModel(
                case_id=input.case_id,
                judge_id=input.judge_id,
                hearing_date=input.hearing_date,
                status=input.status.value if input.status else HearingStatusEnum.SCHEDULED
            )
            
            db.add(new_hearing)
            
            # Update case status to ONGOING if it was FILED
            case = db.query(Case).filter(Case.id == input.case_id).first()
            if case.status == CaseStatusEnum.FILED:
                case.status = CaseStatusEnum.ONGOING
            
            db.commit()
            db.refresh(new_hearing)
            
            return HearingResponse(
                success=True,
                message=format_success_message("scheduled", "hearing"),
                hearing=new_hearing
            )
            
        except Exception as e:
            db.rollback()
            return HearingResponse(
                success=False,
                message=format_error_message("schedule hearing", str(e))
            )
        finally:
            db.close()
    
    @field
    def complete_hearing(self, info: strawberry.Info, hearing_id: int) -> HearingResponse:
        """
        Mark a hearing as completed
        
        Args:
            hearing_id: ID of the hearing to complete
        
        Returns:
            HearingResponse: Response with updated hearing or error
        """
        db = next(get_db())
        try:
            # Get the hearing
            hearing = db.query(HearingModel).filter(HearingModel.id == hearing_id).first()
            if not hearing:
                return HearingResponse(
                    success=False,
                    message=format_error_message("complete hearing", "Hearing not found")
                )
            
            # Check if hearing is already completed
            if hearing.status == HearingStatusEnum.COMPLETED:
                return HearingResponse(
                    success=False,
                    message=format_error_message("complete hearing", "Hearing is already completed")
                )
            
            # Update hearing status
            hearing.status = HearingStatusEnum.COMPLETED
            db.commit()
            db.refresh(hearing)
            
            return HearingResponse(
                success=True,
                message=format_success_message("completed", "hearing"),
                hearing=hearing
            )
            
        except Exception as e:
            db.rollback()
            return HearingResponse(
                success=False,
                message=format_error_message("complete hearing", str(e))
            )
        finally:
            db.close()
    
    @field
    def reschedule_hearing(self, info: strawberry.Info, hearing_id: int, new_date: str) -> HearingResponse:
        """
        Reschedule a hearing to a new date
        
        Args:
            hearing_id: ID of the hearing to reschedule
            new_date: New date in YYYY-MM-DD format
        
        Returns:
            HearingResponse: Response with updated hearing or error
        """
        from datetime import datetime
        
        try:
            date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
        except ValueError:
            return HearingResponse(
                success=False,
                message=format_error_message("reschedule hearing", "Invalid date format. Use YYYY-MM-DD")
            )
        
        db = next(get_db())
        try:
            # Get the hearing
            hearing = db.query(HearingModel).filter(HearingModel.id == hearing_id).first()
            if not hearing:
                return HearingResponse(
                    success=False,
                    message=format_error_message("reschedule hearing", "Hearing not found")
                )
            
            # Check if hearing is already completed
            if hearing.status == HearingStatusEnum.COMPLETED:
                return HearingResponse(
                    success=False,
                    message=format_error_message("reschedule hearing", "Cannot reschedule completed hearing")
                )
            
            # Validate new date is not in past
            date_valid, date_error = validate_date_not_in_past(date_obj)
            if not date_valid:
                return HearingResponse(
                    success=False,
                    message=format_error_message("reschedule hearing", date_error)
                )
            
            # Check for overlapping hearings for the same judge (excluding this hearing)
            if check_hearing_overlap(db, hearing.judge_id, date_obj, exclude_hearing_id=hearing_id):
                return HearingResponse(
                    success=False,
                    message=format_error_message(
                        "reschedule hearing", 
                        "Judge already has a hearing scheduled on the new date"
                    )
                )
            
            # Update hearing date
            old_date = hearing.hearing_date
            hearing.hearing_date = date_obj
            db.commit()
            db.refresh(hearing)
            
            return HearingResponse(
                success=True,
                message=format_success_message(
                    "rescheduled hearing", 
                    f"from {old_date} to {date_obj}"
                ),
                hearing=hearing
            )
            
        except Exception as e:
            db.rollback()
            return HearingResponse(
                success=False,
                message=format_error_message("reschedule hearing", str(e))
            )
        finally:
            db.close()
    
    @field
    def delete_hearing(self, info: strawberry.Info, hearing_id: int) -> HearingResponse:
        """
        Delete a hearing
        
        Args:
            hearing_id: ID of the hearing to delete
        
        Returns:
            HearingResponse: Response with deletion status
        """
        db = next(get_db())
        try:
            # Get the hearing
            hearing = db.query(HearingModel).filter(HearingModel.id == hearing_id).first()
            if not hearing:
                return HearingResponse(
                    success=False,
                    message=format_error_message("delete hearing", "Hearing not found")
                )
            
            # Delete the hearing
            db.delete(hearing)
            db.commit()
            
            return HearingResponse(
                success=True,
                message=format_success_message("deleted", "hearing"),
                hearing=hearing
            )
            
        except Exception as e:
            db.rollback()
            return HearingResponse(
                success=False,
                message=format_error_message("delete hearing", str(e))
            )
        finally:
            db.close()
