"""Knowledge Document Model"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum

from app.db.database import Base


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    TEXT = "text"
    PDF = "pdf"
    WORD = "word"
    IMAGE = "image"
    OTHER = "other"


class KnowledgeDocument(Base):
    """Knowledge documents for astrology knowledge base"""

    __tablename__ = "knowledge_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String(500), nullable=False)  # Storage path
    file_size = Column(Integer, nullable=True)  # Size in bytes
    original_filename = Column(String(255), nullable=True)

    # Vector DB integration
    is_indexed = Column(String(20), default=False)  # Changed to String to store 'true'/'false'
    vector_ids = Column(JSONB, nullable=True)  # Store vector DB IDs for deletion

    # Metadata
    tags = Column(JSONB, nullable=True)  # Array of tags
    doc_metadata = Column(JSONB, nullable=True)  # Additional metadata

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    uploaded_by = Column(UUID(as_uuid=True), nullable=True)  # Admin user ID

    def __repr__(self):
        return f"<KnowledgeDocument {self.title} ({self.document_type})>"
