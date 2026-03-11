"""
Database setup and models for Smart Court Case Management System
"""

import os
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///case_management.db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


# Enum definitions
class CaseStatusEnum:
    FILED = "FILED"
    ONGOING = "ONGOING"
    CLOSED = "CLOSED"


class HearingStatusEnum:
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"


# Database Models
class Case(Base):
    """Case model representing court cases"""
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)
    status = Column(Enum(CaseStatusEnum.FILED, CaseStatusEnum.ONGOING, CaseStatusEnum.CLOSED, name="case_status"), 
                    default=CaseStatusEnum.FILED, nullable=False)
    filed_date = Column(Date, default=date.today, nullable=False)
    
    # Relationships
    hearings = relationship("Hearing", back_populates="case")
    verdicts = relationship("Verdict", back_populates="case")


class Judge(Base):
    """Judge model representing court judges"""
    __tablename__ = "judges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    court_room = Column(String, nullable=False)
    
    # Relationships
    hearings = relationship("Hearing", back_populates="judge")


class Lawyer(Base):
    """Lawyer model representing lawyers"""
    __tablename__ = "lawyers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bar_id = Column(String, unique=True, nullable=False)


class Hearing(Base):
    """Hearing model representing court hearings"""
    __tablename__ = "hearings"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    judge_id = Column(Integer, ForeignKey("judges.id"), nullable=False)
    hearing_date = Column(Date, nullable=False)
    status = Column(Enum(HearingStatusEnum.SCHEDULED, HearingStatusEnum.COMPLETED, name="hearing_status"), 
                    default=HearingStatusEnum.SCHEDULED, nullable=False)
    
    # Relationships
    case = relationship("Case", back_populates="hearings")
    judge = relationship("Judge", back_populates="hearings")


class Verdict(Base):
    """Verdict model representing case verdicts"""
    __tablename__ = "verdicts"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    decision = Column(String, nullable=False)
    decision_date = Column(Date, default=date.today, nullable=False)
    
    # Relationships
    case = relationship("Case", back_populates="verdicts")


# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create all tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    # Create tables when running this file directly
    create_tables()
    print("Database tables created successfully!")
