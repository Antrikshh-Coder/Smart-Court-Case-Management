"""
Utility functions for Smart Court Case Management System
Contains validation logic and helper functions
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session
from db import Case, Hearing, Verdict, CaseStatusEnum, HearingStatusEnum


def check_hearing_overlap(db: Session, judge_id: int, hearing_date: date, exclude_hearing_id: Optional[int] = None) -> bool:
    """
    Check if a judge has overlapping hearings on the same date
    
    Args:
        db: Database session
        judge_id: ID of the judge
        hearing_date: Date of the hearing to check
        exclude_hearing_id: Optional hearing ID to exclude from check (for updates)
    
    Returns:
        bool: True if there's an overlap, False otherwise
    """
    query = db.query(Hearing).filter(
        Hearing.judge_id == judge_id,
        Hearing.hearing_date == hearing_date,
        Hearing.status == HearingStatusEnum.SCHEDULED
    )
    
    # Exclude specific hearing ID if provided (for updates)
    if exclude_hearing_id:
        query = query.filter(Hearing.id != exclude_hearing_id)
    
    overlapping_hearing = query.first()
    return overlapping_hearing is not None


def validate_case_status_transition(current_status: str, new_status: str) -> bool:
    """
    Validate if case status transition is allowed
    
    Args:
        current_status: Current case status
        new_status: New case status to transition to
    
    Returns:
        bool: True if transition is valid, False otherwise
    """
    # Define allowed transitions
    allowed_transitions = {
        CaseStatusEnum.FILED: [CaseStatusEnum.ONGOING],
        CaseStatusEnum.ONGOING: [CaseStatusEnum.CLOSED],
        CaseStatusEnum.CLOSED: []  # No transitions allowed from CLOSED
    }
    
    return new_status in allowed_transitions.get(current_status, [])


def validate_verdict_allowed(db: Session, case_id: int) -> tuple[bool, str]:
    """
    Check if verdict can be recorded for a case
    
    Args:
        db: Database session
        case_id: ID of the case
    
    Returns:
        tuple: (is_allowed, error_message)
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    
    if not case:
        return False, "Case not found"
    
    if case.status != CaseStatusEnum.CLOSED:
        return False, "Verdict can only be recorded for CLOSED cases"
    
    # Check if verdict already exists
    existing_verdict = db.query(Verdict).filter(Verdict.case_id == case_id).first()
    if existing_verdict:
        return False, "Verdict already exists for this case"
    
    return True, ""


def validate_date_not_in_past(input_date: date) -> tuple[bool, str]:
    """
    Validate that a date is not in the past (for scheduling)
    
    Args:
        input_date: Date to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    today = date.today()
    
    if input_date < today:
        return False, "Date cannot be in the past"
    
    return True, ""


def validate_case_exists(db: Session, case_id: int) -> tuple[bool, str]:
    """
    Check if a case exists
    
    Args:
        db: Database session
        case_id: ID of the case
    
    Returns:
        tuple: (exists, error_message)
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    
    if not case:
        return False, "Case not found"
    
    return True, ""


def validate_judge_exists(db: Session, judge_id: int) -> tuple[bool, str]:
    """
    Check if a judge exists
    
    Args:
        db: Database session
        judge_id: ID of the judge
    
    Returns:
        tuple: (exists, error_message)
    """
    judge = db.query(Judge).filter(Judge.id == judge_id).first()
    
    if not judge:
        return False, "Judge not found"
    
    return True, ""


def validate_lawyer_exists(db: Session, lawyer_id: int) -> tuple[bool, str]:
    """
    Check if a lawyer exists
    
    Args:
        db: Database session
        lawyer_id: ID of the lawyer
    
    Returns:
        tuple: (exists, error_message)
    """
    lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
    
    if not lawyer:
        return False, "Lawyer not found"
    
    return True, ""


def validate_hearing_exists(db: Session, hearing_id: int) -> tuple[bool, str]:
    """
    Check if a hearing exists
    
    Args:
        db: Database session
        hearing_id: ID of the hearing
    
    Returns:
        tuple: (exists, error_message)
    """
    hearing = db.query(Hearing).filter(Hearing.id == hearing_id).first()
    
    if not hearing:
        return False, "Hearing not found"
    
    return True, ""


def generate_case_number(db: Session) -> str:
    """
    Generate a unique case number
    
    Args:
        db: Database session
    
    Returns:
        str: Unique case number
    """
    year = datetime.now().year
    case_count = db.query(Case).count()
    case_number = f"CASE-{year}-{case_count + 1:04d}"
    
    # Ensure uniqueness
    while db.query(Case).filter(Case.case_number == case_number).first():
        case_count += 1
        case_number = f"CASE-{year}-{case_count + 1:04d}"
    
    return case_number


def format_error_message(operation: str, error: str) -> str:
    """
    Format error message consistently
    
    Args:
        operation: Operation that failed
        error: Error description
    
    Returns:
        str: Formatted error message
    """
    return f"Failed to {operation}: {error}"


def format_success_message(operation: str, entity: str) -> str:
    """
    Format success message consistently
    
    Args:
        operation: Operation that succeeded
        entity: Entity that was operated on
    
    Returns:
        str: Formatted success message
    """
    return f"Successfully {operation} {entity}"
