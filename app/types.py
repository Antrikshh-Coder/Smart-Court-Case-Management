"""
Strawberry GraphQL types and enums for Smart Court Case Management System
"""

import datetime
from typing import List, Optional
import strawberry


# Enums
from enum import Enum

@strawberry.enum
class CaseStatus(Enum):
    """Case status enum"""
    FILED = "FILED"
    ONGOING = "ONGOING"
    CLOSED = "CLOSED"


@strawberry.enum
class HearingStatus(Enum):
    """Hearing status enum"""
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"


# GraphQL Types
@strawberry.type
class Case:
    """Case GraphQL type"""
    id: int
    case_number: str
    type: str
    status: CaseStatus
    filed_date: datetime.date
    
    # Related fields
    hearings: Optional[List["Hearing"]] = None
    verdicts: Optional[List["Verdict"]] = None


@strawberry.type
class Judge:
    """Judge GraphQL type"""
    id: int
    name: str
    court_room: str
    
    # Related fields
    hearings: Optional[List["Hearing"]] = None


@strawberry.type
class Lawyer:
    """Lawyer GraphQL type"""
    id: int
    name: str
    bar_id: str


@strawberry.type
class Hearing:
    """Hearing GraphQL type"""
    id: int
    case_id: int
    judge_id: int
    hearing_date: datetime.date
    status: HearingStatus
    
    # Related fields
    case: Optional[Case] = None
    judge: Optional[Judge] = None


@strawberry.type
class Verdict:
    """Verdict GraphQL type"""
    id: int
    case_id: int
    decision: str
    decision_date: datetime.date
    
    # Related fields
    case: Optional[Case] = None


# Input Types for Mutations
@strawberry.input
class CaseInput:
    """Input type for creating a case"""
    case_number: str
    type: str
    status: CaseStatus = CaseStatus.FILED
    filed_date: Optional[datetime.date] = None


@strawberry.input
class JudgeInput:
    """Input type for creating a judge"""
    name: str
    court_room: str


@strawberry.input
class LawyerInput:
    """Input type for creating a lawyer"""
    name: str
    bar_id: str


@strawberry.input
class HearingInput:
    """Input type for scheduling a hearing"""
    case_id: int
    judge_id: int
    hearing_date: datetime.date
    status: HearingStatus = HearingStatus.SCHEDULED


@strawberry.input
class VerdictInput:
    """Input type for recording a verdict"""
    case_id: int
    decision: str
    decision_date: Optional[datetime.date] = None


@strawberry.input
class CaseStatusInput:
    """Input type for updating case status"""
    case_id: int
    status: CaseStatus


@strawberry.input
class HearingStatusInput:
    """Input type for updating hearing status"""
    hearing_id: int
    status: HearingStatus


# Response Types
@strawberry.type
class CaseResponse:
    """Response type for case operations"""
    success: bool
    message: str
    case: Optional[Case] = None


@strawberry.type
class JudgeResponse:
    """Response type for judge operations"""
    success: bool
    message: str
    judge: Optional[Judge] = None


@strawberry.type
class LawyerResponse:
    """Response type for lawyer operations"""
    success: bool
    message: str
    lawyer: Optional[Lawyer] = None


@strawberry.type
class HearingResponse:
    """Response type for hearing operations"""
    success: bool
    message: str
    hearing: Optional[Hearing] = None


@strawberry.type
class VerdictResponse:
    """Response type for verdict operations"""
    success: bool
    message: str
    verdict: Optional[Verdict] = None
