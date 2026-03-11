"""
Verdict resolver for Smart Court Case Management System
Handles all verdict-related queries and mutations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from strawberry import field
import strawberry

from db import get_db, Verdict as VerdictModel, Case, CaseStatusEnum
from app.types import Verdict, VerdictInput, VerdictResponse, Case as CaseType
from app.utils import (
    validate_case_exists,
    validate_verdict_allowed,
    format_error_message,
    format_success_message
)


# Query Resolvers
@strawberry.type
class VerdictQuery:
    """Query resolver for verdicts"""
    
    @field
    def get_verdicts(self, info: strawberry.Info) -> List[Verdict]:
        """
        Get all verdicts
        
        Returns:
            List[Verdict]: List of all verdicts
        """
        db = next(get_db())
        try:
            verdicts = db.query(VerdictModel).all()
            return verdicts
        finally:
            db.close()
    
    @field
    def get_verdict_by_id(self, info: strawberry.Info, verdict_id: int) -> Optional[Verdict]:
        """
        Get a verdict by ID
        
        Args:
            verdict_id: ID of the verdict to retrieve
        
        Returns:
            Optional[Verdict]: Verdict if found, None otherwise
        """
        db = next(get_db())
        try:
            verdict = db.query(VerdictModel).filter(VerdictModel.id == verdict_id).first()
            return verdict
        finally:
            db.close()
    
    @field
    def get_verdicts_by_case(self, info: strawberry.Info, case_id: int) -> List[Verdict]:
        """
        Get all verdicts for a specific case
        
        Args:
            case_id: ID of the case
        
        Returns:
            List[Verdict]: List of verdicts for the case
        """
        db = next(get_db())
        try:
            # Validate case exists
            case_exists, error_msg = validate_case_exists(db, case_id)
            if not case_exists:
                return []
            
            verdicts = db.query(VerdictModel).filter(VerdictModel.case_id == case_id).all()
            return verdicts
        finally:
            db.close()
    
    @field
    def get_latest_verdict_for_case(self, info: strawberry.Info, case_id: int) -> Optional[Verdict]:
        """
        Get the latest verdict for a case
        
        Args:
            case_id: ID of the case
        
        Returns:
            Optional[Verdict]: Latest verdict if found, None otherwise
        """
        db = next(get_db())
        try:
            # Validate case exists
            case_exists, error_msg = validate_case_exists(db, case_id)
            if not case_exists:
                return None
            
            verdict = db.query(VerdictModel).filter(VerdictModel.case_id == case_id).order_by(VerdictModel.decision_date.desc()).first()
            return verdict
        finally:
            db.close()
    
    @field
    def get_verdict_history(self, info: strawberry.Info) -> List[Verdict]:
        """
        Get verdict history ordered by decision date
        
        Returns:
            List[Verdict]: List of verdicts ordered by decision date
        """
        db = next(get_db())
        try:
            verdicts = db.query(VerdictModel).order_by(VerdictModel.decision_date.desc()).all()
            return verdicts
        finally:
            db.close()


# Mutation Resolvers
@strawberry.type
class VerdictMutation:
    """Mutation resolver for verdicts"""
    
    @field
    def record_verdict(self, info: strawberry.Info, input: VerdictInput) -> VerdictResponse:
        """
        Record a new verdict for a case
        
        Args:
            input: Verdict input data
        
        Returns:
            VerdictResponse: Response with created verdict or error
        """
        db = next(get_db())
        try:
            # Validate case exists
            case_exists, case_error = validate_case_exists(db, input.case_id)
            if not case_exists:
                return VerdictResponse(
                    success=False,
                    message=format_error_message("record verdict", case_error)
                )
            
            # Validate verdict is allowed for this case
            verdict_allowed, verdict_error = validate_verdict_allowed(db, input.case_id)
            if not verdict_allowed:
                return VerdictResponse(
                    success=False,
                    message=format_error_message("record verdict", verdict_error)
                )
            
            # Create new verdict
            new_verdict = VerdictModel(
                case_id=input.case_id,
                decision=input.decision,
                decision_date=input.decision_date
            )
            
            db.add(new_verdict)
            db.commit()
            db.refresh(new_verdict)
            
            return VerdictResponse(
                success=True,
                message=format_success_message("recorded", "verdict"),
                verdict=new_verdict
            )
            
        except Exception as e:
            db.rollback()
            return VerdictResponse(
                success=False,
                message=format_error_message("record verdict", str(e))
            )
        finally:
            db.close()
    
    @field
    def update_verdict(self, info: strawberry.Info, verdict_id: int, decision: Optional[str] = None, decision_date: Optional[str] = None) -> VerdictResponse:
        """
        Update an existing verdict
        
        Args:
            verdict_id: ID of the verdict to update
            decision: New decision text (optional)
            decision_date: New decision date in YYYY-MM-DD format (optional)
        
        Returns:
            VerdictResponse: Response with updated verdict or error
        """
        from datetime import datetime
        
        db = next(get_db())
        try:
            # Get the verdict
            verdict = db.query(VerdictModel).filter(VerdictModel.id == verdict_id).first()
            if not verdict:
                return VerdictResponse(
                    success=False,
                    message=format_error_message("update verdict", "Verdict not found")
                )
            
            # Update fields if provided
            if decision:
                verdict.decision = decision
            
            if decision_date:
                try:
                    date_obj = datetime.strptime(decision_date, "%Y-%m-%d").date()
                    verdict.decision_date = date_obj
                except ValueError:
                    return VerdictResponse(
                        success=False,
                        message=format_error_message("update verdict", "Invalid date format. Use YYYY-MM-DD")
                    )
            
            db.commit()
            db.refresh(verdict)
            
            return VerdictResponse(
                success=True,
                message=format_success_message("updated", "verdict"),
                verdict=verdict
            )
            
        except Exception as e:
            db.rollback()
            return VerdictResponse(
                success=False,
                message=format_error_message("update verdict", str(e))
            )
        finally:
            db.close()
    
    @field
    def delete_verdict(self, info: strawberry.Info, verdict_id: int) -> VerdictResponse:
        """
        Delete a verdict
        
        Args:
            verdict_id: ID of the verdict to delete
        
        Returns:
            VerdictResponse: Response with deletion status
        """
        db = next(get_db())
        try:
            # Get the verdict
            verdict = db.query(VerdictModel).filter(VerdictModel.id == verdict_id).first()
            if not verdict:
                return VerdictResponse(
                    success=False,
                    message=format_error_message("delete verdict", "Verdict not found")
                )
            
            # Delete the verdict
            db.delete(verdict)
            db.commit()
            
            return VerdictResponse(
                success=True,
                message=format_success_message("deleted", "verdict"),
                verdict=verdict
            )
            
        except Exception as e:
            db.rollback()
            return VerdictResponse(
                success=False,
                message=format_error_message("delete verdict", str(e))
            )
        finally:
            db.close()
    
    @field
    def close_case_with_verdict(self, info: strawberry.Info, case_id: int, decision: str) -> VerdictResponse:
        """
        Close a case and record verdict in one operation
        
        Args:
            case_id: ID of the case to close
            decision: Verdict decision text
        
        Returns:
            VerdictResponse: Response with created verdict or error
        """
        db = next(get_db())
        try:
            # Validate case exists
            case = db.query(Case).filter(Case.id == case_id).first()
            if not case:
                return VerdictResponse(
                    success=False,
                    message=format_error_message("close case with verdict", "Case not found")
                )
            
            # Check if case is already closed
            if case.status == CaseStatusEnum.CLOSED:
                return VerdictResponse(
                    success=False,
                    message=format_error_message("close case with verdict", "Case is already closed")
                )
            
            # Check if verdict already exists
            existing_verdict = db.query(VerdictModel).filter(VerdictModel.case_id == case_id).first()
            if existing_verdict:
                return VerdictResponse(
                    success=False,
                    message=format_error_message("close case with verdict", "Verdict already exists for this case")
                )
            
            # Close the case
            case.status = CaseStatusEnum.CLOSED
            
            # Create new verdict
            new_verdict = VerdictModel(
                case_id=case_id,
                decision=decision,
                decision_date=None  # Will use default (today)
            )
            
            db.add(new_verdict)
            db.commit()
            db.refresh(new_verdict)
            
            return VerdictResponse(
                success=True,
                message=format_success_message("closed case with recorded", "verdict"),
                verdict=new_verdict
            )
            
        except Exception as e:
            db.rollback()
            return VerdictResponse(
                success=False,
                message=format_error_message("close case with verdict", str(e))
            )
        finally:
            db.close()
