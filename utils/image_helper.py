import os
from datetime import datetime
from typing import Optional, Tuple
from PIL import Image
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtCore import QSize, QByteArray
import shutil
import uuid

class ImageHelper:
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}
    MAX_SIZE = (800, 800)  # Maximum dimensions for stored images
    
    @staticmethod
    def save_image(image_path: str, destination_folder: str, image_type: str) -> Optional[str]:
        """
        Save an image to the specified destination folder with proper naming
        Returns the relative path of the saved image
        """
        if not os.path.exists(image_path):
            return None
            
        # Validate file extension
        file_ext = os.path.splitext(image_path)[1].lower()
        if file_ext not in ImageHelper.ALLOWED_EXTENSIONS:
            return None
            
        # Create unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        new_filename = f"{image_type}_{timestamp}_{unique_id}{file_ext}"
        
        # Ensure destination folder exists
        os.makedirs(destination_folder, exist_ok=True)
        
        # Generate destination path
        destination_path = os.path.join(destination_folder, new_filename)
        
        try:
            # Open and process image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if larger than MAX_SIZE
                if img.size[0] > ImageHelper.MAX_SIZE[0] or img.size[1] > ImageHelper.MAX_SIZE[1]:
                    img.thumbnail(ImageHelper.MAX_SIZE, Image.Resampling.LANCZOS)
                
                # Save processed image
                img.save(destination_path, quality=85, optimize=True)
            
            return os.path.relpath(destination_path)
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None
    
    @staticmethod
    def delete_image(image_path: str) -> bool:
        """Delete an image file"""
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                return True
        except Exception as e:
            print(f"Error deleting image: {str(e)}")
        return False
    
    @staticmethod
    def create_thumbnail(image_path: str, size: Tuple[int, int] = (150, 150)) -> Optional[QPixmap]:
        """Create a thumbnail QPixmap from an image file"""
        try:
            if not os.path.exists(image_path):
                return None
                
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Convert PIL image to QPixmap
                img_data = img.tobytes("raw", "RGB")
                qimg = QImage(img_data, img.size[0], img.size[1], QImage.Format_RGB888)
                return QPixmap.fromImage(qimg)
                
        except Exception as e:
            print(f"Error creating thumbnail: {str(e)}")
            return None
    
    @staticmethod
    def validate_image(file_path: str) -> bool:
        """Validate if a file is a valid image"""
        try:
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in ImageHelper.ALLOWED_EXTENSIONS:
                return False
            
            # Try opening the image
            with Image.open(file_path) as img:
                img.verify()
            return True
            
        except Exception:
            return False
            
    @staticmethod
    def get_image_path(relative_path: Optional[str], default_image: str = "default.png") -> str:
        """
        Get the absolute path of an image, returns default image path if the image doesn't exist
        """
        if not relative_path:
            return os.path.join("assets", "images", default_image)
            
        if os.path.exists(relative_path):
            return relative_path
            
        return os.path.join("assets", "images", default_image)
    
    @staticmethod
    def svg_to_png(svg_path: str, size: Tuple[int, int] = (24, 24)) -> Optional[str]:
        """Convert SVG to PNG with specified size"""
        try:
            if not os.path.exists(svg_path) or not svg_path.lower().endswith('.svg'):
                return None
                
            # Read SVG content
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            # Create QImage with transparency
            image = QImage(size[0], size[1], QImage.Format_ARGB32)
            image.fill(0x00000000)  # Transparent background
            
            # Create SVG renderer
            renderer = QSvgRenderer(QByteArray(svg_content.encode()))
            
            # Paint SVG onto image
            painter = QPainter(image)
            renderer.render(painter)
            painter.end()
            
            # Generate output path
            png_path = os.path.splitext(svg_path)[0] + '.png'
            
            # Save as PNG
            image.save(png_path)
            
            return png_path
            
        except Exception as e:
            print(f"Error converting SVG to PNG: {str(e)}")
            return None
    
    @staticmethod
    def convert_all_svg_icons(icons_dir: str) -> None:
        """Convert all SVG icons in a directory to PNG"""
        if not os.path.exists(icons_dir):
            return
            
        for filename in os.listdir(icons_dir):
            if filename.lower().endswith('.svg'):
                svg_path = os.path.join(icons_dir, filename)
                ImageHelper.svg_to_png(svg_path)

# Module-level functions that use the ImageHelper class
def save_image(image_path: str, destination_folder: str, image_type: str) -> Optional[str]:
    """Save an image using the ImageHelper class"""
    return ImageHelper.save_image(image_path, destination_folder, image_type)

def delete_image(image_path: str) -> bool:
    """Delete an image using the ImageHelper class"""
    return ImageHelper.delete_image(image_path)

def create_thumbnail(image_path: str, size: Tuple[int, int] = (150, 150)) -> Optional[QPixmap]:
    """Create a thumbnail using the ImageHelper class"""
    return ImageHelper.create_thumbnail(image_path, size)

def validate_image(file_path: str) -> bool:
    """Validate an image using the ImageHelper class"""
    return ImageHelper.validate_image(file_path)

def get_image_path(relative_path: Optional[str], default_image: str = "default.png") -> str:
    """Get the absolute path of an image using the ImageHelper class"""
    return ImageHelper.get_image_path(relative_path, default_image) 