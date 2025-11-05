# JioAstro Admin Portal

## Overview

The Admin Portal provides comprehensive administrative capabilities for managing the JioAstro platform, including knowledge base enrichment and user management.

## Features

### 1. Admin Authentication
- Secure login with username/password
- JWT-based token authentication
- Session management with automatic redirect

### 2. Knowledge Bank Management
- **Upload Documents**: Support for text, PDF, Word documents, and images (max 50MB)
- **Document Metadata**: Title, description, tags for organization
- **Document List**: View all uploaded documents with status
- **Document Delete**: Remove documents from the knowledge base
- **Integration**: Uploaded documents integrate with existing training pipeline

### 3. User Management
- **View All Users**: List all user profiles in the system
- **User Details**: View birth information and creation dates
- **Delete Users**: Remove user profiles and associated data
- **Password Reset**: Initiate password reset for users

## Access

### Default Credentials
- **Username**: `admin`
- **Email**: `admin@jioastro.com`
- **Password**: `admin@123`

You can log in with either username or email.

⚠️ **IMPORTANT**: Change the default password immediately after first login!

### Login URL
```
http://localhost:3000/admin/login
```

## Setup Instructions

### 1. Backend Setup

#### Create Database Tables and Admin User

Run the admin initialization script:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python scripts/create_admin_user.py
```

This will:
- Create the `admin_users` table
- Create the `knowledge_documents` table
- Insert the default admin user (admin/admin@123)

#### Verify Backend is Running

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

Backend should be accessible at: `http://localhost:8000`

### 2. Frontend Setup

#### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend should be accessible at: `http://localhost:3000`

### 3. Access Admin Portal

1. Navigate to `http://localhost:3000/admin/login`
2. Login with credentials: `admin` / `admin@123`
3. You'll be redirected to the admin dashboard

## Usage Guide

### Uploading Knowledge Documents

1. Navigate to the "Knowledge Bank" tab
2. Click "Upload Knowledge Document"
3. Fill in the form:
   - **File**: Select your file (text, PDF, Word, or image)
   - **Title**: Give it a descriptive title
   - **Document Type**: Select the appropriate type
   - **Description**: Optional description
   - **Tags**: Optional comma-separated tags (e.g., "planets, houses, yogas")
4. Click "Upload Document"
5. The document will be saved and marked for indexing

**Note**: After upload, documents need to be processed through the ingestion pipeline to be indexed into the vector database. This integration point is marked with TODO in the code.

### Managing Documents

- **View Documents**: All uploaded documents appear in the list below the upload form
- **Document Status**: Shows whether document is "Indexed" or "Pending"
- **Delete Document**: Click the trash icon to remove a document
- **Refresh List**: Click the refresh icon to reload the document list

### Managing Users

1. Switch to the "User Management" tab
2. View all user profiles with their:
   - Name
   - Birth date and location
   - Account creation date
3. Delete users by clicking the trash icon
4. Use the refresh button to reload the user list

## API Endpoints

### Admin Authentication

```
POST /api/v1/admin/login
Body: { "username": "admin", "password": "admin@123" }
Response: { "access_token": "...", "admin_id": "...", "username": "..." }
```

### Knowledge Bank Management

```
GET /api/v1/admin/knowledge?limit=100
Headers: Authorization: Bearer <admin_token>

POST /api/v1/admin/knowledge/upload
Headers: Authorization: Bearer <admin_token>
Body: multipart/form-data with file and metadata

DELETE /api/v1/admin/knowledge/{document_id}
Headers: Authorization: Bearer <admin_token>
```

### User Management

```
GET /api/v1/admin/users?limit=100
Headers: Authorization: Bearer <admin_token>

DELETE /api/v1/admin/users/{user_id}
Headers: Authorization: Bearer <admin_token>

POST /api/v1/admin/users/reset-password
Headers: Authorization: Bearer <admin_token>
Body: { "user_id": "...", "new_password": "..." }
```

## Security Considerations

1. **Change Default Password**: Immediately change the default admin password
2. **Token Storage**: Admin tokens are stored in localStorage
3. **Token Expiry**: Tokens expire after 7 days (configurable in backend)
4. **HTTPS**: Use HTTPS in production
5. **Rate Limiting**: Consider implementing rate limiting for admin endpoints
6. **Audit Logging**: Consider adding audit logs for admin actions

## File Upload Specifications

- **Maximum File Size**: 50MB
- **Supported Formats**:
  - Text: `.txt`
  - PDF: `.pdf`
  - Word: `.doc`, `.docx`
  - Images: `.jpg`, `.jpeg`, `.png`
- **Storage Location**: `backend/uploads/knowledge_documents/`

## Troubleshooting

### Cannot Login

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check if admin user was created: Run initialization script again
3. Check browser console for errors
4. Verify credentials are correct

### Documents Not Uploading

1. Check file size (must be < 50MB)
2. Check file format is supported
3. Verify admin token is valid
4. Check backend logs for errors
5. Ensure `uploads/knowledge_documents/` directory exists

### Users Not Loading

1. Verify Supabase connection is working
2. Check if profiles table has data
3. Check admin token authorization
4. Review backend logs

## Integration with Training Pipeline

The admin portal uploads documents and stores metadata in the database. To integrate with the existing training pipeline:

1. **Manual Processing**: After upload, manually run the ingestion script:
   ```bash
   cd backend
   python scripts/ingest_comprehensive_rules.py
   ```

2. **Automatic Processing** (TODO): Implement automatic triggering of ingestion pipeline after document upload in `/api/v1/admin/knowledge/upload` endpoint

3. **Status Updates**: Update `is_indexed` field and `vector_ids` after successful ingestion

## Future Enhancements

- [ ] Automatic ingestion pipeline trigger after upload
- [ ] Document preview/download
- [ ] Bulk document operations
- [ ] User activity monitoring
- [ ] Admin activity audit logs
- [ ] Document version control
- [ ] Advanced search and filtering
- [ ] Analytics dashboard
- [ ] Multi-admin support with roles

## Technical Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Database**: PostgreSQL via Supabase
- **File Storage**: Local filesystem (can be migrated to S3/cloud storage)
- **Models**: SQLAlchemy ORM

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **State Management**: React hooks + localStorage
- **API Client**: Fetch API

### Security Features
- Password hashing with bcrypt
- JWT token authentication
- Token expiry (7 days default)
- Protected routes with middleware
- Admin-only API endpoints

## Support

For issues or questions about the admin portal, please check:
- Backend logs: `backend/logs/`
- Frontend console: Browser developer tools
- Database: Supabase dashboard

## License

Part of the JioAstro project.
