"""
Case resolver for Smart Court Case Management System
Handles all case-related queries and mutations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from strawberry import field
import strawberry
from db import get_db, Case as CaseModel, CaseStatusEnum
from app.types import Case, CaseInput, CaseResponse, CaseStatus
from app.utils import (
    validate_case_status_transition,
    format_error_message,
    format_success_message,
    generate_case_number
)


# Query Resolvers
@strawberry.type
class CaseQuery:
    """Query resolver for cases"""
    
    @field
    def get_cases(self, info: strawberry.Info) -> List[Case]:
        """
        Get all cases
        
        Returns:
            List[Case]: List of all cases
        """
        db = next(get_db())
        try:
            cases = db.query(CaseModel).all()
            return cases
        finally:
            db.close()
    
    @field
    def get_case_by_id(self, info: strawberry.Info, case_id: int) -> Optional[Case]:
        """
        Get a case by ID
        
        Args:
            case_id: ID of the case to retrieve
        
        Returns:
            Optional[Case]: Case if found, None otherwise
        """
        db = next(get_db())
        try:
            case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
            return case
        finally:
            db.close()
    
    @field
    def get_cases_by_status(self, info: strawberry.Info, status: CaseStatus) -> List[Case]:
        """
        Get cases by status
        
        Args:
            status: Status to filter cases by
        
        Returns:
            List[Case]: List of cases with the specified status
        """
        db = next(get_db())
        try:
            cases = db.query(CaseModel).filter(CaseModel.status == status.value).all()
            return cases
        finally:
            db.close()


# Mutation Resolvers
@strawberry.type
class CaseMutation:
    """Mutation resolver for cases"""
    
    @field
    def create_case(self, info: strawberry.Info, input: CaseInput) -> CaseResponse:
        """
        Create a new case
        
        Args:
            input: Case input data
        
        Returns:
            CaseResponse: Response with created case or error
        """
        db = next(get_db())
        try:
            # Check if case number already exists
            existing_case = db.query(CaseModel).filter(CaseModel.case_number == input.case_number).first()
            if existing_case:
                return CaseResponse(
                    success=False,
                    message=format_error_message("create case", "Case number already exists")
                )
            
            # Create new case
            new_case = CaseModel(
                case_number=input.case_number,
                type=input.type,
                status=input.status.value if input.status else CaseStatusEnum.FILED,
                filed_date=input.filed_date
            )
            
            db.add(new_case)
            db.commit()
            db.refresh(new_case)
            
            return CaseResponse(
                success=True,
                message=format_success_message("created", "case"),
                case=new_case
            )
            
        except Exception as e:
            db.rollback()
            return CaseResponse(
                success=False,
                message=format_error_message("create case", str(e))
            )
        finally:
            db.close()
    
    @field
    def update_case_status(self, info: strawberry.Info, case_id: int, new_status: CaseStatus) -> CaseResponse:
        """
        Update case status
        
        Args:
            case_id: ID of the case to update
            new_status: New status for the case
        
        Returns:
            CaseResponse: Response with updated case or error
        """
        db = next(get_db())
        try:
            # Get the case
            case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
            if not case:
                return CaseResponse(
                    success=False,
                    message=format_error_message("update case status", "Case not found")
                )
            
            # Validate status transition
            if not validate_case_status_transition(case.status, new_status.value):
                return CaseResponse(
                    success=False,
                    message=format_error_message(
                        "update case status", 
                        f"Invalid status transition from {case.status} to {new_status.value}"
                    )
                )
            
            # Update status
            old_status = case.status
            case.status = new_status.value
            db.commit()
            db.refresh(case)
            
            return CaseResponse(
                success=True,
                message=format_success_message(
                    "updated case status", 
                    f"from {old_status} to {new_status.value}"
                ),
                case=case
            )
            
        except Exception as e:
            db.rollback()
            return CaseResponse(
                success=False,
                message=format_error_message("update case status", str(e))
            )
        finally:
            db.close()
    
    @field
    def create_case_with_auto_number(self, info: strawberry.Info, case_type: str) -> CaseResponse:
        """
        Create a new case with auto-generated case number
        
        Args:
            case_type: Type of the case
        
        Returns:
            CaseResponse: Response with created case or error
        """
        db = next(get_db())
        try:
            # Generate unique case number
            case_number = generate_case_number(db)
            
            # Create new case
            new_case = CaseModel(
                case_number=case_number,
                type=case_type,
                status=CaseStatusEnum.FILED,
                filed_date=None  # Will use default
            )
            
            db.add(new_case)
            db.commit()
            db.refresh(new_case)
            
            return CaseResponse(
                success=True,
                message=format_success_message("created", f"case with number {case_number}"),
                case=new_case
            )
            
        except Exception as e:
            db.rollback()
            return CaseResponse(
                success=False,
                message=format_error_message("create case", str(e))
            )
        finally:
            db.close()
