-- Create Palmistry Storage Buckets
-- This migration creates the storage buckets needed for palmistry images

-- Create palm-images bucket for full-size images
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'palm-images',
  'palm-images',
  false, -- private bucket, requires authentication
  10485760, -- 10MB limit
  ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO UPDATE
SET
  public = false,
  file_size_limit = 10485760,
  allowed_mime_types = ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

-- Create palm-thumbnails bucket for thumbnails
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'palm-thumbnails',
  'palm-thumbnails',
  true, -- public bucket for faster loading
  1048576, -- 1MB limit for thumbnails
  ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
)
ON CONFLICT (id) DO UPDATE
SET
  public = true,
  file_size_limit = 1048576,
  allowed_mime_types = ARRAY['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

-- ============================================
-- Storage Policies for palm-images bucket
-- ============================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can upload their own palm images" ON storage.objects;
DROP POLICY IF EXISTS "Users can view their own palm images" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own palm images" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own palm images" ON storage.objects;

-- Policy: Users can upload their own palm images
CREATE POLICY "Users can upload their own palm images"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'palm-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Users can view their own palm images
CREATE POLICY "Users can view their own palm images"
ON storage.objects
FOR SELECT
TO authenticated
USING (
  bucket_id = 'palm-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Users can update their own palm images
CREATE POLICY "Users can update their own palm images"
ON storage.objects
FOR UPDATE
TO authenticated
USING (
  bucket_id = 'palm-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
)
WITH CHECK (
  bucket_id = 'palm-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Users can delete their own palm images
CREATE POLICY "Users can delete their own palm images"
ON storage.objects
FOR DELETE
TO authenticated
USING (
  bucket_id = 'palm-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- ============================================
-- Storage Policies for palm-thumbnails bucket
-- ============================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can upload their own palm thumbnails" ON storage.objects;
DROP POLICY IF EXISTS "Anyone can view palm thumbnails" ON storage.objects;
DROP POLICY IF EXISTS "Users can update their own palm thumbnails" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own palm thumbnails" ON storage.objects;

-- Policy: Users can upload their own palm thumbnails
CREATE POLICY "Users can upload their own palm thumbnails"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'palm-thumbnails' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Anyone can view palm thumbnails (public bucket)
CREATE POLICY "Anyone can view palm thumbnails"
ON storage.objects
FOR SELECT
TO public
USING (bucket_id = 'palm-thumbnails');

-- Policy: Users can update their own palm thumbnails
CREATE POLICY "Users can update their own palm thumbnails"
ON storage.objects
FOR UPDATE
TO authenticated
USING (
  bucket_id = 'palm-thumbnails' AND
  (storage.foldername(name))[1] = auth.uid()::text
)
WITH CHECK (
  bucket_id = 'palm-thumbnails' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Policy: Users can delete their own palm thumbnails
CREATE POLICY "Users can delete their own palm thumbnails"
ON storage.objects
FOR DELETE
TO authenticated
USING (
  bucket_id = 'palm-thumbnails' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- ============================================
-- Summary
-- ============================================

-- View created buckets
SELECT
  id,
  name,
  public,
  file_size_limit,
  allowed_mime_types
FROM storage.buckets
WHERE id IN ('palm-images', 'palm-thumbnails')
ORDER BY id;

COMMENT ON TABLE storage.buckets IS 'Storage buckets configuration';
