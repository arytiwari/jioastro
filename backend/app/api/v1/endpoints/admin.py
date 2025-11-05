"""Admin endpoints for authentication and management - Using Supabase REST API"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from datetime import datetime
import uuid
import os
import shutil
import asyncio
from pathlib import Path

from app.schemas.admin import (
    AdminLogin,
    AdminLoginResponse,
    AdminResponse,
    AdminPasswordReset
)
from app.schemas.knowledge_document import (
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse
)
from app.schemas.profile import ProfileResponse
from app.core.admin_security import (
    verify_password,
    create_admin_access_token,
    get_current_admin
)
from app.services.supabase_service import supabase_service
from app.services.document_processor import document_processor

router = APIRouter()

# File upload configuration
UPLOAD_DIR = Path("uploads/knowledge_documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


# ============================================
# Admin Authentication
# ============================================

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(login_data: AdminLogin):
    """Admin login endpoint - accepts username or email"""
    # Find admin user by username or email using Supabase REST API
    admin = await supabase_service.get_admin_by_username_or_email(login_data.username)

    if not admin or not verify_password(login_data.password, admin["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
        )

    if not admin.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    # Update last login
    await supabase_service.update_admin_last_login(admin["id"])

    # Create access token
    access_token = create_admin_access_token(
        data={"sub": str(admin["id"]), "username": admin["username"]}
    )

    return AdminLoginResponse(
        access_token=access_token,
        admin_id=str(admin["id"]),
        username=admin["username"]
    )


@router.get("/me")
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    """Get current admin user information"""
    return current_admin


# ============================================
# User Management
# ============================================

@router.get("/users")
async def list_all_users(
    limit: int = 100,
    offset: int = 0,
    current_admin: dict = Depends(get_current_admin)
):
    """List all user profiles (admin only)"""
    profiles = await supabase_service.get_all_profiles_admin(limit=limit, offset=offset)
    return profiles


@router.delete("/users/{profile_id}")
async def delete_user_profile(
    profile_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a user profile (admin only)"""
    try:
        # Check if profile exists
        profile = await supabase_service.get_profile(profile_id=profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Delete from Supabase (admin can delete without user_id check)
        success = await supabase_service.delete_profile(profile_id=profile_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete profile"
            )

        return {"message": "User profile deleted successfully", "profile_id": profile_id}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.post("/users/reset-password")
async def reset_user_password(
    reset_data: AdminPasswordReset,
    current_admin: dict = Depends(get_current_admin)
):
    """Reset a user's password (admin only)"""
    try:
        # This would typically integrate with Supabase Auth API
        # For now, return success message
        # TODO: Implement Supabase Auth password reset
        return {
            "message": "Password reset initiated. User will receive reset email.",
            "user_id": reset_data.user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )


# ============================================
# Knowledge Bank Management
# ============================================

@router.post("/knowledge/upload", response_model=DocumentResponse)
async def upload_knowledge_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(None),
    document_type: str = Form(...),
    tags: str = Form(None),  # Comma-separated tags
    current_admin: dict = Depends(get_current_admin)
):
    """Upload a knowledge document"""
    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {MAX_FILE_SIZE / (1024*1024)}MB"
        )

    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

    # Parse tags
    tags_list = [tag.strip() for tag in tags.split(",")] if tags else []

    # Create document record using Supabase REST API
    document_data = {
        "title": title,
        "description": description,
        "document_type": document_type,
        "file_path": str(file_path),
        "file_size": file_size,
        "original_filename": file.filename,
        "is_indexed": "false",  # Will be indexed by ingestion pipeline
        "tags": tags_list,
        "uploaded_by": current_admin["id"]
    }

    new_document = await supabase_service.create_knowledge_document(document_data)

    if not new_document:
        # Clean up file if database insert failed
        try:
            file_path.unlink()
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create document record"
        )

    # Trigger background processing
    print(f"📄 Document uploaded: {title} ({file.filename})")
    print(f"🔄 Starting background processing for document ID: {new_document['id']}")

    # Start processing in background (fire and forget)
    asyncio.create_task(document_processor.process_document(new_document['id']))

    return new_document


@router.get("/knowledge", response_model=DocumentListResponse)
async def list_knowledge_documents(
    limit: int = 50,
    offset: int = 0,
    document_type: str = None,
    current_admin: dict = Depends(get_current_admin)
):
    """List all knowledge documents"""
    documents, total = await supabase_service.get_knowledge_documents(
        document_type=document_type,
        limit=limit,
        offset=offset
    )

    return DocumentListResponse(
        documents=documents,
        total=total,
        offset=offset,
        limit=limit
    )


@router.get("/knowledge/{document_id}", response_model=DocumentResponse)
async def get_knowledge_document(
    document_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Get a specific knowledge document"""
    document = await supabase_service.get_knowledge_document(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.patch("/knowledge/{document_id}", response_model=DocumentResponse)
async def update_knowledge_document(
    document_id: str,
    update_data: DocumentUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update knowledge document metadata"""
    # Build update dict
    update_dict = {}
    if update_data.title is not None:
        update_dict["title"] = update_data.title
    if update_data.description is not None:
        update_dict["description"] = update_data.description
    if update_data.tags is not None:
        update_dict["tags"] = update_data.tags

    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    updated_document = await supabase_service.update_knowledge_document(
        document_id,
        update_dict
    )

    if not updated_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return updated_document


@router.delete("/knowledge/{document_id}")
async def delete_knowledge_document(
    document_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Delete a knowledge document"""
    # Get document first to get file path
    document = await supabase_service.get_knowledge_document(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Delete file from disk
    try:
        file_path = Path(document["file_path"])
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"⚠️ Failed to delete file: {str(e)}")

    # TODO: Remove from vector database if indexed
    if document.get("vector_ids"):
        print(f"⚠️ Manual vector DB cleanup required for document ID: {document_id}")

    # Delete from database
    success = await supabase_service.delete_knowledge_document(document_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )

    return {"message": "Document deleted successfully", "document_id": document_id}


@router.post("/knowledge/{document_id}/process")
async def process_knowledge_document(
    document_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """Manually trigger processing/indexing for a document"""
    # Check if document exists
    document = await supabase_service.get_knowledge_document(document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check if already processing
    if document.get("is_indexed") == "processing":
        return {
            "message": "Document is already being processed",
            "document_id": document_id,
            "status": "processing"
        }

    # Start processing in background
    print(f"🔄 Manual processing triggered for document ID: {document_id}")
    asyncio.create_task(document_processor.process_document(document_id))

    return {
        "message": "Processing started",
        "document_id": document_id,
        "status": "processing"
    }
