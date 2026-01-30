"""
Image Service

Business logic for image upload and processing operations.
"""

import os
import uuid
from werkzeug.utils import secure_filename


# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Upload folders (in common directory)
UPLOAD_FOLDER = "../common/uploads/backend"
FRONTEND_UPLOAD_FOLDER = "../common/uploads/frontend"

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(FRONTEND_UPLOAD_FOLDER, exist_ok=True)


class ImageService:
    """Service class for image-related operations"""
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        Check if file has an allowed extension.
        
        Args:
            filename: Name of the file
            
        Returns:
            bool: True if file extension is allowed
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_uploaded_image(file_content: bytes, filename: str) -> str:
        """
        Save uploaded image file securely.
        
        Args:
            file_content: File content in bytes
            filename: Original filename
            
        Returns:
            str: Path to saved file
        """
        # Generate secure filename
        secure_name = secure_filename(f"{uuid.uuid4()}_{filename}")
        file_path = os.path.join(UPLOAD_FOLDER, secure_name)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Delete a file from filesystem.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            bool: True if file was deleted successfully
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Failed to remove file {file_path}: {str(e)}")
            return False
    
    @staticmethod
    def validate_file_size(content: bytes, max_size_mb: int) -> tuple:
        """
        Validate file size.
        
        Args:
            content: File content in bytes
            max_size_mb: Maximum allowed size in MB
            
        Returns:
            tuple: (is_valid, error_message)
        """
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            return False, f"File too large. Maximum size allowed: {max_size_mb}MB"
        
        return True, None
