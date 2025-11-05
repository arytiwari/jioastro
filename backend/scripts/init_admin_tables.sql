-- Admin User Initialization SQL Script
-- Run this script in your Supabase SQL Editor

-- Create admin_users table
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    CONSTRAINT admin_users_username_check CHECK (length(username) >= 3)
);

-- Create knowledge_documents table
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_type VARCHAR(20) NOT NULL CHECK (document_type IN ('text', 'pdf', 'word', 'image', 'other')),
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    original_filename VARCHAR(255),
    is_indexed VARCHAR(20) DEFAULT 'false',
    vector_ids JSONB,
    tags JSONB,
    doc_metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    uploaded_by UUID REFERENCES admin_users(id) ON DELETE SET NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_type ON knowledge_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_created ON knowledge_documents(created_at DESC);

-- Insert default admin user
-- Password is bcrypt hash of "admin@123"
INSERT INTO admin_users (username, password_hash, email, is_active)
VALUES (
    'admin',
    '$2b$12$VfT74mgelw3D6La6ASwGBeuHJbEPtWWzyVBk5tYB8LyVuxrAOotj.',  -- This is hash of "admin@123"
    'admin@jioastro.com',
    true
)
ON CONFLICT (username)
DO UPDATE SET
    password_hash = '$2b$12$VfT74mgelw3D6La6ASwGBeuHJbEPtWWzyVBk5tYB8LyVuxrAOotj.',
    email = 'admin@jioastro.com',
    is_active = true;

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON admin_users TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON knowledge_documents TO authenticated;

-- Success message
SELECT 'Admin tables created successfully!' as message;
SELECT 'Default admin user: admin / admin@123' as credentials;
