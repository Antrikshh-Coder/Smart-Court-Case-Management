"""
Main FastAPI application for Smart Court Case Management System
Provides GraphQL API endpoint using Strawberry GraphQL
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from db import create_tables
from schema import schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Creates database tables on startup
    """
    # Create database tables
    print("Creating database tables...")
    create_tables()
    print("Database tables created successfully!")
    
    yield
    
    print("Application shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Smart Court Case Management System",
    description="A GraphQL API for managing court cases, judges, lawyers, hearings, and verdicts",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Mount GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Smart Court Case Management System API",
        "version": "1.0.0",
        "graphql_endpoint": "/graphql",
        "docs": {
            "graphql_playground": "http://localhost:8000/graphql",
            "description": "Use the GraphQL Playground to explore the API"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Smart Court Case Management System",
        "version": "1.0.0"
    }


# API info endpoint
@app.get("/info")
async def api_info():
    """
    API information endpoint
    """
    return {
        "name": "Smart Court Case Management System",
        "description": "A comprehensive GraphQL API for court case management",
        "features": [
            "Case management with status tracking",
            "Judge and lawyer management",
            "Hearing scheduling with overlap validation",
            "Verdict recording and history",
            "Case status transitions",
            "Real-time GraphQL API"
        ],
        "available_queries": [
            "getCases - Get all cases",
            "getCaseById - Get a case by ID",
            "getJudges - Get all judges",
            "getLawyers - Get all lawyers",
            "getHearingsByCase - Get hearings for a case",
            "getVerdictsByCase - Get verdicts for a case",
            "getJudgeCases - Get cases for a judge",
            "getScheduledHearings - Get scheduled hearings"
        ],
        "available_mutations": [
            "createCase - Create a new case",
            "createJudge - Add a new judge",
            "createLawyer - Add a new lawyer",
            "scheduleHearing - Schedule a hearing",
            "completeHearing - Mark hearing as completed",
            "recordVerdict - Record a verdict",
            "updateCaseStatus - Update case status",
            "rescheduleHearing - Reschedule a hearing"
        ],
        "validations": [
            "Prevent overlapping hearings for same judge",
            "Enforce case status transitions (FILED → ONGOING → CLOSED)",
            "Verdict only allowed when case is CLOSED",
            "Date validation for scheduling",
            "Unique constraints on case numbers and bar IDs"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
