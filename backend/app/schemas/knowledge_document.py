"""Knowledge Document schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class DocumentUpload(BaseModel):
    """Document upload metadata"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    document_type: str = Field(..., description="Document type: text, pdf, word, image")
    tags: Optional[List[str]] = None


class DocumentUpdate(BaseModel):
    """Update document metadata"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentResponse(BaseModel):
    """Knowledge document response"""
    id: UUID
    title: str
    description: Optional[str]
    document_type: str
    file_path: str
    file_size: Optional[int]
    original_filename: Optional[str]
    is_indexed: bool
    tags: Optional[List[str]]
    doc_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    uploaded_by: Optional[UUID]

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """List of documents with pagination"""
    documents: List[DocumentResponse]
    total: int
    offset: int
    limit: int
