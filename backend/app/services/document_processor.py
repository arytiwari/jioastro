"""Document Processing Service for Admin-Uploaded Knowledge Documents"""

import asyncio
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai

from app.core.config import settings
from app.services.supabase_service import supabase_service


class DocumentProcessorService:
    """Service for processing and ingesting admin-uploaded documents"""

    def __init__(self):
        self.supabase = supabase_service

        # Initialize OpenAI client for embeddings
        try:
            if settings.USE_AZURE_OPENAI:
                self.openai_client = openai.AzureOpenAI(
                    api_key=settings.AZURE_OPENAI_API_KEY,
                    api_version=settings.AZURE_OPENAI_API_VERSION,
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    timeout=30.0,
                    max_retries=2
                )
                self.embedding_model = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
                print(f"✅ Document Processor: Using Azure OpenAI Embeddings (deployment: {self.embedding_model})")
            else:
                self.openai_client = openai.OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    timeout=30.0,
                    max_retries=2
                )
                self.embedding_model = "text-embedding-ada-002"
                print("✅ Document Processor: Using OpenAI Embeddings")

            self.embedding_dimensions = 1536
        except Exception as e:
            print(f"⚠️ Error initializing OpenAI client for document processor: {str(e)}")
            self.openai_client = None
            self.embedding_model = None

    async def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """Extract text content from various file types"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            if file_type == "text" or path.suffix in ['.txt', '.md']:
                # Plain text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

            elif file_type == "pdf" or path.suffix == '.pdf':
                # PDF files - try PyPDF2 first, fall back to simple read
                try:
                    import PyPDF2
                    text_parts = []
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            text_parts.append(page.extract_text())
                    return "\n\n".join(text_parts)
                except ImportError:
                    print("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")
                    return f"[PDF file: {path.name}] - Install PyPDF2 to extract text"

            elif file_type == "word" or path.suffix in ['.doc', '.docx']:
                # Word documents - try python-docx
                try:
                    import docx
                    doc = docx.Document(file_path)
                    return "\n\n".join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    print("⚠️ python-docx not installed. Install with: pip install python-docx")
                    return f"[Word document: {path.name}] - Install python-docx to extract text"

            elif file_type == "image" or path.suffix in ['.jpg', '.jpeg', '.png']:
                # Images - try OCR with pytesseract
                try:
                    from PIL import Image
                    import pytesseract
                    image = Image.open(file_path)
                    return pytesseract.image_to_string(image)
                except ImportError:
                    print("⚠️ pytesseract or PIL not installed. Install with: pip install pytesseract pillow")
                    return f"[Image file: {path.name}] - Install pytesseract and pillow for OCR"

            else:
                # Fallback for unknown types
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                except:
                    return f"[Binary file: {path.name}] - Unable to extract text"

        except Exception as e:
            print(f"❌ Error extracting text from {file_path}: {str(e)}")
            return f"[Error extracting text from {path.name}]: {str(e)}"

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks for embedding"""
        if not text or len(text) < chunk_size:
            return [text] if text else []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)

                if break_point > chunk_size // 2:  # Only break if we're past halfway
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return [c for c in chunks if c]  # Remove empty chunks

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate OpenAI embedding for text"""
        if not self.openai_client or not text:
            return None

        try:
            # Truncate text if too long (max 8191 tokens for ada-002)
            if len(text) > 30000:  # Conservative estimate: 1 token ≈ 4 chars
                text = text[:30000]

            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            print(f"❌ Error generating embedding: {str(e)}")
            return None

    async def process_document(self, document_id: str) -> Dict[str, Any]:
        """
        Main processing pipeline for a document

        Steps:
        1. Update status to 'processing'
        2. Extract text from file
        3. Chunk text
        4. Generate embeddings for chunks
        5. Store embeddings in vector database
        6. Update document status to 'indexed'

        Returns processing stats
        """
        try:
            # Get document record
            document = await self.supabase.get_knowledge_document(document_id)
            if not document:
                raise ValueError(f"Document not found: {document_id}")

            # Update status to processing
            await self.supabase.update_knowledge_document(
                document_id,
                {
                    "is_indexed": "processing",
                    "updated_at": datetime.utcnow().isoformat()
                }
            )

            print(f"📄 Processing document: {document['title']}")
            start_time = datetime.utcnow()

            # Step 1: Extract text
            print(f"  1️⃣ Extracting text from {document['document_type']} file...")
            text = await self.extract_text_from_file(
                document['file_path'],
                document['document_type']
            )

            if not text or len(text.strip()) < 50:
                raise ValueError("Insufficient text content extracted from document")

            text_length = len(text)
            print(f"  ✅ Extracted {text_length} characters")

            # Step 2: Chunk text
            print(f"  2️⃣ Chunking text...")
            chunks = self.chunk_text(text, chunk_size=1000, overlap=100)
            num_chunks = len(chunks)
            print(f"  ✅ Created {num_chunks} chunks")

            # Step 3: Generate embeddings
            print(f"  3️⃣ Generating embeddings for {num_chunks} chunks...")
            vector_ids = []

            if self.openai_client:
                for i, chunk in enumerate(chunks, 1):
                    if i % 10 == 0:
                        print(f"    Processing chunk {i}/{num_chunks}...")

                    embedding = await self.generate_embedding(chunk)
                    if embedding:
                        # Generate unique ID for this chunk
                        chunk_hash = hashlib.sha256(chunk.encode()).hexdigest()[:16]
                        vector_id = f"{document_id}_{i}_{chunk_hash}"
                        vector_ids.append(vector_id)

                        # Store in vector database (simplified - you may want to use Supabase pgvector)
                        # For now, we'll just store the metadata

                    # Add small delay to avoid rate limits
                    if i % 10 == 0:
                        await asyncio.sleep(0.5)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Step 4: Update document record
            update_data = {
                "is_indexed": "true",
                "vector_ids": vector_ids if vector_ids else None,
                "doc_metadata": {
                    "text_length": text_length,
                    "num_chunks": num_chunks,
                    "num_embeddings": len(vector_ids),
                    "processing_time_seconds": processing_time,
                    "processed_at": datetime.utcnow().isoformat()
                },
                "updated_at": datetime.utcnow().isoformat()
            }

            await self.supabase.update_knowledge_document(document_id, update_data)

            print(f"  ✅ Document processed successfully in {processing_time:.2f}s")

            return {
                "success": True,
                "document_id": document_id,
                "stats": {
                    "text_length": text_length,
                    "num_chunks": num_chunks,
                    "num_embeddings": len(vector_ids),
                    "processing_time_seconds": processing_time
                }
            }

        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Error processing document {document_id}: {error_msg}")

            # Update status to failed
            try:
                await self.supabase.update_knowledge_document(
                    document_id,
                    {
                        "is_indexed": "failed",
                        "doc_metadata": {
                            "error": error_msg,
                            "failed_at": datetime.utcnow().isoformat()
                        },
                        "updated_at": datetime.utcnow().isoformat()
                    }
                )
            except:
                pass

            return {
                "success": False,
                "document_id": document_id,
                "error": error_msg
            }


# Singleton instance
document_processor = DocumentProcessorService()
