"""
Lawyer resolver for Smart Court Case Management System
Handles all lawyer-related queries and mutations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from strawberry import field
import strawberry
from db import get_db, Lawyer as LawyerModel
from app.types import Lawyer, LawyerInput, LawyerResponse
from app.utils import (
    validate_lawyer_exists,
    format_error_message,
    format_success_message
)


# Query Resolvers
@strawberry.type
class LawyerQuery:
    """Query resolver for lawyers"""
    
    @field
    def get_lawyers(self, info: strawberry.Info) -> List[Lawyer]:
        """
        Get all lawyers
        
        Returns:
            List[Lawyer]: List of all lawyers
        """
        db = next(get_db())
        try:
            lawyers = db.query(LawyerModel).all()
            return lawyers
        finally:
            db.close()
    
    @field
    def get_lawyer_by_id(self, info: strawberry.Info, lawyer_id: int) -> Optional[Lawyer]:
        """
        Get a lawyer by ID
        
        Args:
            lawyer_id: ID of the lawyer to retrieve
        
        Returns:
            Optional[Lawyer]: Lawyer if found, None otherwise
        """
        db = next(get_db())
        try:
            lawyer = db.query(LawyerModel).filter(LawyerModel.id == lawyer_id).first()
            return lawyer
        finally:
            db.close()
    
    @field
    def get_lawyer_by_bar_id(self, info: strawberry.Info, bar_id: str) -> Optional[Lawyer]:
        """
        Get a lawyer by bar ID
        
        Args:
            bar_id: Bar ID of the lawyer to retrieve
        
        Returns:
            Optional[Lawyer]: Lawyer if found, None otherwise
        """
        db = next(get_db())
        try:
            lawyer = db.query(LawyerModel).filter(LawyerModel.bar_id == bar_id).first()
            return lawyer
        finally:
            db.close()
    
    @field
    def search_lawyers_by_name(self, info: strawberry.Info, name: str) -> List[Lawyer]:
        """
        Search lawyers by name (partial match)
        
        Args:
            name: Name or partial name to search for
        
        Returns:
            List[Lawyer]: List of lawyers matching the name
        """
        db = next(get_db())
        try:
            lawyers = db.query(LawyerModel).filter(LawyerModel.name.ilike(f"%{name}%")).all()
            return lawyers
        finally:
            db.close()


# Mutation Resolvers
@strawberry.type
class LawyerMutation:
    """Mutation resolver for lawyers"""
    
    @field
    def create_lawyer(self, info: strawberry.Info, input: LawyerInput) -> LawyerResponse:
        """
        Create a new lawyer
        
        Args:
            input: Lawyer input data
        
        Returns:
            LawyerResponse: Response with created lawyer or error
        """
        db = next(get_db())
        try:
            # Check if bar ID already exists
            existing_lawyer = db.query(LawyerModel).filter(LawyerModel.bar_id == input.bar_id).first()
            if existing_lawyer:
                return LawyerResponse(
                    success=False,
                    message=format_error_message("create lawyer", "Lawyer with this bar ID already exists")
                )
            
            # Check if lawyer with same name already exists
            existing_name = db.query(LawyerModel).filter(LawyerModel.name == input.name).first()
            if existing_name:
                return LawyerResponse(
                    success=False,
                    message=format_error_message("create lawyer", "Lawyer with this name already exists")
                )
            
            # Create new lawyer
            new_lawyer = LawyerModel(
                name=input.name,
                bar_id=input.bar_id
            )
            
            db.add(new_lawyer)
            db.commit()
            db.refresh(new_lawyer)
            
            return LawyerResponse(
                success=True,
                message=format_success_message("created", "lawyer"),
                lawyer=new_lawyer
            )
            
        except Exception as e:
            db.rollback()
            return LawyerResponse(
                success=False,
                message=format_error_message("create lawyer", str(e))
            )
        finally:
            db.close()
    
    @field
    def update_lawyer(self, info: strawberry.Info, lawyer_id: int, name: Optional[str] = None, bar_id: Optional[str] = None) -> LawyerResponse:
        """
        Update lawyer information
        
        Args:
            lawyer_id: ID of the lawyer to update
            name: New name (optional)
            bar_id: New bar ID (optional)
        
        Returns:
            LawyerResponse: Response with updated lawyer or error
        """
        db = next(get_db())
        try:
            # Get the lawyer
            lawyer = db.query(LawyerModel).filter(LawyerModel.id == lawyer_id).first()
            if not lawyer:
                return LawyerResponse(
                    success=False,
                    message=format_error_message("update lawyer", "Lawyer not found")
                )
            
            # Update fields if provided
            if name:
                # Check if another lawyer has this name
                existing_lawyer = db.query(LawyerModel).filter(
                    LawyerModel.name == name,
                    LawyerModel.id != lawyer_id
                ).first()
                if existing_lawyer:
                    return LawyerResponse(
                        success=False,
                        message=format_error_message("update lawyer", "Another lawyer with this name already exists")
                    )
                lawyer.name = name
            
            if bar_id:
                # Check if another lawyer has this bar ID
                existing_bar_id = db.query(LawyerModel).filter(
                    LawyerModel.bar_id == bar_id,
                    LawyerModel.id != lawyer_id
                ).first()
                if existing_bar_id:
                    return LawyerResponse(
                        success=False,
                        message=format_error_message("update lawyer", "Another lawyer with this bar ID already exists")
                    )
                lawyer.bar_id = bar_id
            
            db.commit()
            db.refresh(lawyer)
            
            return LawyerResponse(
                success=True,
                message=format_success_message("updated", "lawyer"),
                lawyer=lawyer
            )
            
        except Exception as e:
            db.rollback()
            return LawyerResponse(
                success=False,
                message=format_error_message("update lawyer", str(e))
            )
        finally:
            db.close()
    
    @field
    def delete_lawyer(self, info: strawberry.Info, lawyer_id: int) -> LawyerResponse:
        """
        Delete a lawyer
        
        Args:
            lawyer_id: ID of the lawyer to delete
        
        Returns:
            LawyerResponse: Response with deletion status
        """
        db = next(get_db())
        try:
            # Get the lawyer
            lawyer = db.query(LawyerModel).filter(LawyerModel.id == lawyer_id).first()
            if not lawyer:
                return LawyerResponse(
                    success=False,
                    message=format_error_message("delete lawyer", "Lawyer not found")
                )
            
            # Delete the lawyer
            db.delete(lawyer)
            db.commit()
            
            return LawyerResponse(
                success=True,
                message=format_success_message("deleted", "lawyer"),
                lawyer=lawyer
            )
            
        except Exception as e:
            db.rollback()
            return LawyerResponse(
                success=False,
                message=format_error_message("delete lawyer", str(e))
            )
        finally:
            db.close()
