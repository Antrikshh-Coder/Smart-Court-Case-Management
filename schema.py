"""
GraphQL Schema for Smart Court Case Management System
Combines all query and mutation resolvers
"""

import strawberry
from app.resolvers.case_resolver import CaseQuery, CaseMutation
from app.resolvers.judge_resolver import JudgeQuery, JudgeMutation
from app.resolvers.lawyer_resolver import LawyerQuery, LawyerMutation
from app.resolvers.hearing_resolver import HearingQuery, HearingMutation
from app.resolvers.verdict_resolver import VerdictQuery, VerdictMutation


# Combine all query resolvers
@strawberry.type
class Query(CaseQuery, JudgeQuery, LawyerQuery, HearingQuery, VerdictQuery):
    """
    Root Query type that combines all query resolvers
    Includes queries for cases, judges, lawyers, hearings, and verdicts
    """
    pass


# Combine all mutation resolvers
@strawberry.type
class Mutation(CaseMutation, JudgeMutation, LawyerMutation, HearingMutation, VerdictMutation):
    """
    Root Mutation type that combines all mutation resolvers
    Includes mutations for cases, judges, lawyers, hearings, and verdicts
    """
    pass


# Create the complete schema
schema = strawberry.Schema(query=Query, mutation=Mutation)


# Export schema for use in main.py
__all__ = ["schema", "Query", "Mutation"]
