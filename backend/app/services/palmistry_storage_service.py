"""
Palmistry Image Storage Service.

Handles image upload, validation, thumbnail generation, and storage management
for palm images using Supabase Storage.
"""

import base64
import hashlib
import io
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

from PIL import Image, ImageFilter, ImageStat
from supabase import create_client, Client

from app.core.config import settings
from app.schemas.palmistry import ImageValidation


logger = logging.getLogger(__name__)


class PalmistryStorageService:
    """
    Service for managing palm image storage operations.

    Handles:
    - Image upload to Supabase Storage
    - Image quality validation
    - Thumbnail generation
    - Image metadata extraction
    - Image cleanup and deletion
    """

    # Storage configuration
    STORAGE_BUCKET = "palm-images"
    THUMBNAIL_BUCKET = "palm-thumbnails"
    THUMBNAIL_SIZE = (300, 300)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_IMAGE_SIZE = 50 * 1024  # 50KB
    SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}

    # Quality thresholds
    MIN_QUALITY_SCORE = 40.0
    MIN_FOCUS_SCORE = 30.0
    MIN_LIGHTING_SCORE = 25.0

    def __init__(self):
        """Initialize Supabase client for storage operations."""
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY  # Use service role for backend operations
        )

    async def upload_palm_image(
        self,
        image_data: str,
        user_id: str,  # Changed from UUID to str
        hand_type: str,
        view_type: str,
        device_info: Optional[Dict] = None
    ) -> Tuple[str, str, Dict, ImageValidation]:
        """
        Upload palm image to storage and generate thumbnail.

        Args:
            image_data: Base64 encoded image or data URL
            user_id: User ID as string
            hand_type: "left" or "right"
            view_type: "front", "back", "zoomed", "thumb_edge", "side"
            device_info: Optional device metadata

        Returns:
            Tuple of (image_url, thumbnail_url, metadata, validation_result)

        Raises:
            ValueError: If image validation fails
            Exception: If upload fails
        """
        try:
            # 1. Decode and validate image
            image, image_bytes = self._decode_image(image_data)

            # 2. Validate image size
            self._validate_image_size(len(image_bytes))

            # 3. Extract metadata
            metadata = self._extract_metadata(image, device_info)

            # 4. Validate image quality
            validation = await self._validate_image_quality(image)

            if validation.quality_score < self.MIN_QUALITY_SCORE:
                raise ValueError(
                    f"Image quality too low ({validation.quality_score:.1f}). "
                    f"Minimum required: {self.MIN_QUALITY_SCORE}"
                )

            # 5. Generate file paths
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(image_bytes).hexdigest()[:8]
            user_id_str = str(user_id)
            filename = f"{user_id_str}/{hand_type}_{view_type}_{timestamp}_{file_hash}.jpg"
            thumb_filename = f"{user_id_str}/{hand_type}_{view_type}_{timestamp}_{file_hash}_thumb.jpg"

            # 6. Upload full image
            image_url = await self._upload_to_storage(
                image_bytes,
                filename,
                self.STORAGE_BUCKET
            )

            # 7. Generate and upload thumbnail
            thumbnail_bytes = self._generate_thumbnail(image)
            thumbnail_url = await self._upload_to_storage(
                thumbnail_bytes,
                thumb_filename,
                self.THUMBNAIL_BUCKET
            )

            logger.info(
                f"Successfully uploaded palm image: user={user_id}, "
                f"hand={hand_type}, view={view_type}, quality={validation.quality_score:.1f}"
            )

            return image_url, thumbnail_url, metadata, validation

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to upload palm image: {str(e)}")
            raise Exception(f"Image upload failed: {str(e)}")

    def _decode_image(self, image_data: str) -> Tuple[Image.Image, bytes]:
        """
        Decode base64 image data.

        Args:
            image_data: Base64 encoded image or data URL

        Returns:
            Tuple of (PIL Image, raw bytes)

        Raises:
            ValueError: If image cannot be decoded
        """
        try:
            # Remove data URL prefix if present
            if image_data.startswith("data:image"):
                image_data = image_data.split(",", 1)[1]

            # Decode base64
            image_bytes = base64.b64decode(image_data)

            # Open with PIL
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if necessary
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")

            return image, image_bytes

        except Exception as e:
            raise ValueError(f"Invalid image data: {str(e)}")

    def _validate_image_size(self, size_bytes: int) -> None:
        """
        Validate image file size.

        Args:
            size_bytes: Image size in bytes

        Raises:
            ValueError: If size is invalid
        """
        if size_bytes < self.MIN_IMAGE_SIZE:
            raise ValueError(
                f"Image too small ({size_bytes / 1024:.1f}KB). "
                f"Minimum: {self.MIN_IMAGE_SIZE / 1024:.1f}KB"
            )

        if size_bytes > self.MAX_IMAGE_SIZE:
            raise ValueError(
                f"Image too large ({size_bytes / 1024 / 1024:.1f}MB). "
                f"Maximum: {self.MAX_IMAGE_SIZE / 1024 / 1024:.1f}MB"
            )

    def _extract_metadata(
        self,
        image: Image.Image,
        device_info: Optional[Dict]
    ) -> Dict:
        """
        Extract image metadata including EXIF and computed properties.

        Args:
            image: PIL Image object
            device_info: Optional device information

        Returns:
            Dictionary of metadata
        """
        metadata = {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
            "size_bytes": len(image.tobytes()),
            "aspect_ratio": round(image.width / image.height, 2),
        }

        # Extract EXIF data if available
        if hasattr(image, "_getexif") and image._getexif():
            exif = image._getexif()
            if exif:
                metadata["exif"] = {
                    k: str(v) for k, v in exif.items() if k in [
                        "Make", "Model", "DateTime", "Flash",
                        "ExposureTime", "FNumber", "ISOSpeedRatings"
                    ]
                }

        # Add device info
        if device_info:
            metadata["device"] = device_info

        return metadata

    async def _validate_image_quality(self, image: Image.Image) -> ImageValidation:
        """
        Validate image quality using multiple metrics.

        Args:
            image: PIL Image object

        Returns:
            ImageValidation object with scores and suggestions
        """
        # Calculate individual quality metrics
        focus_score = self._calculate_focus_quality(image)
        lighting_score = self._calculate_lighting_quality(image)

        # Overall quality is weighted average
        quality_score = (focus_score * 0.6) + (lighting_score * 0.4)

        # Determine quality levels
        focus_quality = self._score_to_quality(focus_score)
        lighting_quality = self._score_to_quality(lighting_score)

        # Generate suggestions
        suggestions = []
        if focus_score < 50:
            suggestions.append("Image is blurry. Hold camera steady and ensure good focus.")
        if lighting_score < 40:
            suggestions.append("Lighting is poor. Move to a well-lit area or use flash.")
        if image.width < 800 or image.height < 800:
            suggestions.append("Image resolution is low. Use higher quality camera settings.")

        # Hand detection will be done by AI service
        is_hand_detected = True  # Placeholder - actual detection in AI service

        return ImageValidation(
            is_hand_detected=is_hand_detected,
            focus_quality=focus_quality,
            lighting_quality=lighting_quality,
            suggestions=suggestions,
            quality_score=round(quality_score, 1)
        )

    def _calculate_focus_quality(self, image: Image.Image) -> float:
        """
        Calculate image focus/sharpness quality using Laplacian variance.

        Args:
            image: PIL Image object

        Returns:
            Focus quality score (0-100)
        """
        try:
            # Convert to grayscale
            gray = image.convert("L")

            # Apply Laplacian filter to detect edges
            laplacian = gray.filter(ImageFilter.FIND_EDGES)

            # Calculate variance (higher = sharper)
            stat = ImageStat.Stat(laplacian)
            variance = stat.var[0]

            # Normalize to 0-100 scale
            # Typical sharp images have variance > 100
            # Blurry images have variance < 50
            score = min(100, (variance / 200) * 100)

            return score

        except Exception as e:
            logger.warning(f"Focus quality calculation failed: {e}")
            return 50.0  # Default to medium quality

    def _calculate_lighting_quality(self, image: Image.Image) -> float:
        """
        Calculate lighting quality based on brightness and contrast.

        Args:
            image: PIL Image object

        Returns:
            Lighting quality score (0-100)
        """
        try:
            # Convert to grayscale
            gray = image.convert("L")

            # Calculate statistics
            stat = ImageStat.Stat(gray)
            mean_brightness = stat.mean[0]
            stddev = stat.stddev[0]

            # Ideal brightness is 120-140 (on 0-255 scale)
            # Ideal std dev is 40-60 (good contrast)
            brightness_score = 100 - abs(130 - mean_brightness) * 1.5
            contrast_score = min(100, stddev * 2)

            # Weighted average
            score = (brightness_score * 0.6) + (contrast_score * 0.4)
            score = max(0, min(100, score))

            return score

        except Exception as e:
            logger.warning(f"Lighting quality calculation failed: {e}")
            return 50.0  # Default to medium quality

    def _score_to_quality(self, score: float) -> str:
        """Convert numeric score to quality label."""
        if score >= 75:
            return "excellent"
        elif score >= 55:
            return "good"
        elif score >= 35:
            return "fair"
        else:
            return "poor"

    def _generate_thumbnail(self, image: Image.Image) -> bytes:
        """
        Generate thumbnail from image.

        Args:
            image: PIL Image object

        Returns:
            Thumbnail as bytes
        """
        # Create thumbnail
        thumbnail = image.copy()
        thumbnail.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

        # Convert to JPEG bytes
        buffer = io.BytesIO()
        thumbnail.save(buffer, format="JPEG", quality=85, optimize=True)
        return buffer.getvalue()

    async def _upload_to_storage(
        self,
        file_bytes: bytes,
        filename: str,
        bucket: str
    ) -> str:
        """
        Upload file to Supabase Storage.

        Args:
            file_bytes: File content as bytes
            filename: Destination filename/path
            bucket: Storage bucket name

        Returns:
            Public URL of uploaded file

        Raises:
            Exception: If upload fails
        """
        try:
            # Upload to Supabase Storage
            response = self.supabase.storage.from_(bucket).upload(
                path=filename,
                file=file_bytes,
                file_options={"content-type": "image/jpeg"}
            )

            # Get public URL
            public_url = self.supabase.storage.from_(bucket).get_public_url(filename)

            return public_url

        except Exception as e:
            logger.error(f"Storage upload failed: {str(e)}")
            raise Exception(f"Failed to upload to storage: {str(e)}")

    async def delete_palm_image(
        self,
        image_url: str,
        thumbnail_url: Optional[str] = None
    ) -> bool:
        """
        Delete palm image and thumbnail from storage.

        Args:
            image_url: Full image URL
            thumbnail_url: Optional thumbnail URL

        Returns:
            True if successful

        Raises:
            Exception: If deletion fails
        """
        try:
            # Extract filename from URL
            image_filename = self._extract_filename_from_url(image_url)

            # Delete main image
            self.supabase.storage.from_(self.STORAGE_BUCKET).remove([image_filename])

            # Delete thumbnail if provided
            if thumbnail_url:
                thumb_filename = self._extract_filename_from_url(thumbnail_url)
                self.supabase.storage.from_(self.THUMBNAIL_BUCKET).remove([thumb_filename])

            logger.info(f"Deleted palm image: {image_filename}")
            return True

        except Exception as e:
            logger.error(f"Image deletion failed: {str(e)}")
            raise Exception(f"Failed to delete image: {str(e)}")

    def _extract_filename_from_url(self, url: str) -> str:
        """Extract filename from Supabase public URL."""
        # URL format: https://[project].supabase.co/storage/v1/object/public/[bucket]/[filename]
        parts = url.split("/public/")
        if len(parts) == 2:
            # Remove bucket name and get filename
            return "/".join(parts[1].split("/")[1:])
        raise ValueError(f"Invalid storage URL format: {url}")

    async def get_image_stats(self, user_id: str) -> Dict:
        """
        Get storage statistics for a user.

        Args:
            user_id: User ID as string

        Returns:
            Dictionary with storage stats
        """
        try:
            # List all files for user
            files = self.supabase.storage.from_(self.STORAGE_BUCKET).list(str(user_id))

            total_size = sum(f.get("metadata", {}).get("size", 0) for f in files)
            total_count = len(files)

            return {
                "total_images": total_count,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_bucket": self.STORAGE_BUCKET
            }

        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}")
            return {
                "total_images": 0,
                "total_size_mb": 0.0,
                "error": str(e)
            }
