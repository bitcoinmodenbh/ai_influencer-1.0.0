#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image Generation Module for AI Influencer System

This module handles the generation of images for the AI Influencer system, including:
- Creating images based on post content
- Customizing images for different topics
- Ensuring proper image sizing for Twitter
- Adding text overlays and branding
"""

import os
import random
import logging
import tempfile
from typing import Dict, List, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
from io import BytesIO
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("image_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ImageGenerator")

class ImageGenerator:
    """
    Class to handle image generation for the AI Influencer system.
    """
    
    # Define image themes for different categories
    THEMES = {
        "Bitcoin": {
            "colors": ["#F7931A", "#4D4D4D", "#FFFFFF", "#000000"],  # Bitcoin orange, gray, white, black
            "backgrounds": ["blockchain", "bitcoin", "finance", "technology"],
            "icons": ["bitcoin", "blockchain", "chart", "wallet"]
        },
        "Lightning Network": {
            "colors": ["#792EE5", "#FFFFFF", "#000000", "#F7931A"],  # Lightning purple, white, black, Bitcoin orange
            "backgrounds": ["network", "lightning", "technology", "speed"],
            "icons": ["lightning", "network", "payment", "channel"]
        },
        "Nostr": {
            "colors": ["#8E44AD", "#FFFFFF", "#000000", "#3498DB"],  # Purple, white, black, blue
            "backgrounds": ["social", "network", "communication", "decentralized"],
            "icons": ["relay", "profile", "message", "connection"]
        },
        "Privacy": {
            "colors": ["#2C3E50", "#ECF0F1", "#000000", "#3498DB"],  # Dark blue, light gray, black, blue
            "backgrounds": ["security", "privacy", "protection", "encryption"],
            "icons": ["shield", "lock", "key", "mask"]
        },
        "Node Setup": {
            "colors": ["#27AE60", "#FFFFFF", "#000000", "#F1C40F"],  # Green, white, black, yellow
            "backgrounds": ["server", "hardware", "network", "configuration"],
            "icons": ["server", "node", "hardware", "terminal"]
        }
    }
    
    # Define standard image sizes
    IMAGE_SIZES = {
        "twitter": (1200, 675),  # 16:9 aspect ratio for Twitter
        "square": (1080, 1080),  # Square format for flexibility
        "portrait": (1080, 1350)  # 4:5 aspect ratio for portrait
    }
    
    def __init__(self, assets_dir: Optional[str] = None):
        """
        Initialize the Image Generator.
        
        Args:
            assets_dir: Directory containing image assets (optional)
        """
        # Load .env file if it exists
        load_dotenv()
        
        # Set assets directory
        self.assets_dir = assets_dir or os.path.join(os.path.dirname(__file__), 'assets')
        
        # Create assets directory if it doesn't exist
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, 'backgrounds'), exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, 'icons'), exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, 'fonts'), exist_ok=True)
        
        # Initialize font paths
        self.font_regular = self._get_font_path('regular')
        self.font_bold = self._get_font_path('bold')
        
        logger.info(f"Initialized ImageGenerator with assets directory: {self.assets_dir}")
    
    def _get_font_path(self, font_type: str) -> str:
        """
        Get the path to a font file, downloading it if necessary.
        
        Args:
            font_type: Type of font ('regular' or 'bold')
            
        Returns:
            str: Path to the font file
        """
        font_dir = os.path.join(self.assets_dir, 'fonts')
        
        # Define font files and URLs
        font_files = {
            'regular': 'OpenSans-Regular.ttf',
            'bold': 'OpenSans-Bold.ttf'
        }
        
        font_urls = {
            'regular': 'https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Regular.ttf',
            'bold': 'https://github.com/google/fonts/raw/main/apache/opensans/OpenSans-Bold.ttf'
        }
        
        font_file = font_files.get(font_type, 'OpenSans-Regular.ttf')
        font_path = os.path.join(font_dir, font_file)
        
        # Download font if it doesn't exist
        if not os.path.exists(font_path):
            try:
                url = font_urls.get(font_type)
                if url:
                    logger.info(f"Downloading font: {font_file}")
                    response = requests.get(url)
                    with open(font_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"Font downloaded: {font_path}")
                else:
                    # Use default system font if URL not available
                    logger.warning(f"No URL for font type: {font_type}, using system default")
                    font_path = None
            except Exception as e:
                logger.error(f"Error downloading font: {str(e)}")
                font_path = None
        
        return font_path
    
    def _get_background_image(self, category: str) -> Optional[Image.Image]:
        """
        Get a background image for the specified category.
        
        Args:
            category: Topic category
            
        Returns:
            PIL.Image.Image: Background image
        """
        backgrounds_dir = os.path.join(self.assets_dir, 'backgrounds')
        
        # Get theme for the category
        theme = self.THEMES.get(category, self.THEMES["Bitcoin"])
        
        # Look for background images matching the theme
        background_files = []
        for bg_type in theme["backgrounds"]:
            # Check for files with the background type in the name
            for file in os.listdir(backgrounds_dir):
                if bg_type.lower() in file.lower() and file.endswith(('.jpg', '.jpeg', '.png')):
                    background_files.append(os.path.join(backgrounds_dir, file))
        
        # If no matching backgrounds found, use any available background
        if not background_files:
            background_files = [os.path.join(backgrounds_dir, f) for f in os.listdir(backgrounds_dir)
                              if f.endswith(('.jpg', '.jpeg', '.png'))]
        
        # If still no backgrounds, generate a simple one
        if not background_files:
            logger.warning(f"No background images found for category: {category}, generating simple background")
            return self._generate_simple_background(category)
        
        # Select a random background
        background_path = random.choice(background_files)
        
        try:
            # Open and return the background image
            return Image.open(background_path)
        except Exception as e:
            logger.error(f"Error opening background image: {str(e)}")
            return self._generate_simple_background(category)
    
    def _generate_simple_background(self, category: str) -> Image.Image:
        """
        Generate a simple background image for the specified category.
        
        Args:
            category: Topic category
            
        Returns:
            PIL.Image.Image: Generated background image
        """
        # Get theme colors for the category
        theme = self.THEMES.get(category, self.THEMES["Bitcoin"])
        colors = theme["colors"]
        
        # Create a gradient background
        width, height = self.IMAGE_SIZES["twitter"]
        image = Image.new('RGB', (width, height), colors[0])
        draw = ImageDraw.Draw(image)
        
        # Draw some random shapes for visual interest
        for _ in range(20):
            shape_type = random.choice(['circle', 'rectangle'])
            color = random.choice(colors[1:])
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(20, 200)
            
            if shape_type == 'circle':
                draw.ellipse((x, y, x + size, y + size), fill=color)
            else:
                draw.rectangle((x, y, x + size, y + size), fill=color)
        
        # Apply blur to make it less harsh
        image = image.filter(ImageFilter.GaussianBlur(radius=10))
        
        return image
    
    def _get_icon_image(self, category: str) -> Optional[Image.Image]:
        """
        Get an icon image for the specified category.
        
        Args:
            category: Topic category
            
        Returns:
            PIL.Image.Image: Icon image or None if not found
        """
        icons_dir = os.path.join(self.assets_dir, 'icons')
        
        # Get theme for the category
        theme = self.THEMES.get(category, self.THEMES["Bitcoin"])
        
        # Look for icon images matching the theme
        icon_files = []
        for icon_type in theme["icons"]:
            # Check for files with the icon type in the name
            for file in os.listdir(icons_dir):
                if icon_type.lower() in file.lower() and file.endswith(('.png', '.svg')):
                    icon_files.append(os.path.join(icons_dir, file))
        
        # If no matching icons found, return None
        if not icon_files:
            return None
        
        # Select a random icon
        icon_path = random.choice(icon_files)
        
        try:
            # Open and return the icon image
            return Image.open(icon_path)
        except Exception as e:
            logger.error(f"Error opening icon image: {str(e)}")
            return None
    
    def _create_chart_image(self, category: str) -> Image.Image:
        """
        Create a chart image for the specified category.
        
        Args:
            category: Topic category
            
        Returns:
            PIL.Image.Image: Generated chart image
        """
        # Get theme colors for the category
        theme = self.THEMES.get(category, self.THEMES["Bitcoin"])
        colors = theme["colors"]
        
        # Create a matplotlib figure
        plt.figure(figsize=(12, 6.75), facecolor=colors[2])
        
        # Generate random data based on category
        if category == "Bitcoin":
            # Price chart
            days = 30
            x = np.arange(days)
            trend = np.cumsum(np.random.normal(0.5, 1, days))
            plt.plot(x, trend, color=colors[0], linewidth=3)
            plt.title("Bitcoin Price Trend", fontsize=24, color=colors[1])
            plt.ylabel("Price (USD)", fontsize=16, color=colors[1])
            plt.xlabel("Days", fontsize=16, color=colors[1])
            
        elif category == "Lightning Network":
            # Network growth
            x = np.arange(10)
            y = np.exp(x / 2) * 100
            plt.bar(x, y, color=colors[0])
            plt.title("Lightning Network Growth", fontsize=24, color=colors[1])
            plt.ylabel("Nodes", fontsize=16, color=colors[1])
            plt.xlabel("Time", fontsize=16, color=colors[1])
            
        elif category == "Nostr":
            # User adoption
            x = np.arange(12)
            y1 = np.exp(x / 4) * 50
            y2 = np.exp(x / 5) * 30
            plt.plot(x, y1, color=colors[0], linewidth=3, label="Users")
            plt.plot(x, y2, color=colors[3], linewidth=3, label="Relays")
            plt.legend(fontsize=14)
            plt.title("Nostr Ecosystem Growth", fontsize=24, color=colors[1])
            plt.ylabel("Count", fontsize=16, color=colors[1])
            plt.xlabel("Months", fontsize=16, color=colors[1])
            
        elif category == "Privacy":
            # Privacy metrics
            labels = ['High', 'Medium', 'Low']
            sizes = [45, 30, 25]
            plt.pie(sizes, labels=labels, colors=[colors[0], colors[3], colors[1]], 
                   autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title("Privacy Levels in Cryptocurrency Users", fontsize=20, color=colors[1])
            
        else:
            # Node setup difficulty
            categories = ['Hardware', 'Software', 'Maintenance', 'Security']
            values = [3, 4, 2, 5]
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            values += values[:1]
            angles += angles[:1]
            categories += categories[:1]
            
            ax = plt.subplot(111, polar=True)
            ax.plot(angles, values, color=colors[0], linewidth=2)
            ax.fill(angles, values, color=colors[0], alpha=0.25)
            ax.set_thetagrids(np.degrees(angles[:-1]), categories[:-1])
            plt.title("Node Setup Complexity", fontsize=24, color=colors[1])
        
        # Adjust style
        plt.grid(alpha=0.3)
        plt.tight_layout()
        
        # Save to BytesIO
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        
        # Convert to PIL Image
        buf.seek(0)
        return Image.open(buf)
    
    def _add_text_overlay(self, image: Image.Image, text: str, category: str) -> Image.Image:
        """
        Add text overlay to an image.
        
        Args:
            image: Base image
            text: Text to overlay
            category: Topic category
            
        Returns:
            PIL.Image.Image: Image with text overlay
        """
        # Get theme colors for the category
        theme = self.THEMES.get(category, self.THEMES["Bitcoin"])
        colors = theme["colors"]
        
        # Create a copy of the image
        result = image.copy()
        draw = ImageDraw.Draw(result)
        
        # Determine text size and position
        width, height = image.size
        
        # Limit text length
        if len(text) > 100:
            text = text[:97] + "..."
        
        # Try to use custom font, fall back to default
        try:
            if self.font_bold:
                title_font = ImageFont.truetype(self.font_bold, size=48)
            else:
                title_font = ImageFont.load_default()
                
            if self.font_regular:
                body_font = ImageFont.truetype(self.font_regular, size=36)
            else:
                body_font = ImageFont.load_default()
        except Exception as e:
            logger.error(f"Error loading font: {str(e)}")
            title_font = ImageFont.load_default()
            body_font = title_font
        
        # Split text into title and body
        parts = text.split('. ', 1)
        if len(parts) > 1:
            title, body = parts
            title += '.'
        else:
            title = text
            body = ""
        
        # Add semi-transparent background for text
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Calculate text positions
        padding = 20
        text_box_height = height // 3
        text_box_y = height - text_box_height - padding
        
        # Draw text background
        overlay_draw.rectangle(
            [(padding, text_box_y), (width - padding, height - padding)],
            fill=(0, 0, 0, 180)
        )
        
        # Composite the overlay onto the image
        result = Image.alpha_composite(result.convert('RGBA'), overlay)
        result_draw = ImageDraw.Draw(result)
        
        # Draw title text
        title_y = text_box_y + padding
        result_draw.text((padding * 2, title_y), title, font=title_font, fill=colors[1])
        
        # Draw body text if available
        if body:
            body_y = title_y + title_font.getsize(title)[1] + padding
            result_draw.text((padding * 2, body_y), body, font=body_font, fill=colors[1])
        
        # Add category label
        label_padding = 10
        label_height = 40
        label_y = padding
        label_width = title_font.getsize(category)[0] + label_padding * 4
        
        # Draw label background
        result_draw.rectangle(
            [(padding, label_y), (padding + label_width, label_y + label_height)],
            fill=colors[0]
        )
        
        # Draw label text
        result_draw.text(
            (padding + label_padding * 2, label_y + label_padding),
            category,
            font=body_font,
            fill=colors[1]
        )
        
        return result.convert('RGB')
    
    def _add_branding(self, image: Image.Image) -> Image.Image:
        """
        Add branding elements to an image.
        
        Args:
            image: Base image
            
        Returns:
            PIL.Image.Image: Image with branding
        """
        # Create a copy of the image
        result = image.copy()
        draw = ImageDraw.Draw(result)
        
        # Get image dimensions
        width, height = image.size
        
        # Add watermark text
        try:
            if self.font_regular:
                watermark_font = ImageFont.truetype(self.font_regular, size=24)
            else:
                watermark_font = ImageFont.load_default()
                
            watermark_text = "AI Influencer"
            text_width = watermark_font.getsize(watermark_text)[0]
            
            # Position in bottom right corner
            text_x = width - text_width - 20
            text_y = height - 40
            
            # Draw semi-transparent background
            text_bg_padding = 5
            draw.rectangle(
                [(text_x - text_bg_padding, text_y - text_bg_padding),
                 (text_x + text_width + text_bg_padding, text_y + 30)],
                fill=(0, 0, 0, 128)
            )
            
            # Draw text
            draw.text((text_x, text_y), watermark_text, font=watermark_font, fill=(255, 255, 255, 200))
            
        except Exception as e:
            logger.error(f"Error adding branding: {str(e)}")
        
        return result
    
    def _resize_image(self, image: Image.Image, size_key: str = "twitter") -> Image.Image:
        """
        Resize image to standard dimensions.
        
        Args:
            image: Image to resize
            size_key: Key for standard size ('twitter', 'square', or 'portrait')
            
        Returns:
            PIL.Image.Image: Resized image
        """
        target_size = self.IMAGE_SIZES.get(size_key, self.IMAGE_SIZES["twitter"])
        
        # Calculate aspect ratios
        img_aspect = image.width / image.height
        target_aspect = target_size[0] / target_size[1]
        
        # Determine dimensions to crop to
        if img_aspect > target_aspect:
            # Image is wider than target
            new_width = int(image.height * target_aspect)
            new_height = image.height
            left = (image.width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = new_height
        else:
            # Image is taller than target
            new_width = image.width
            new_height = int(image.width / target_aspect)
            left = 0
            top = (image.height - new_height) // 2
            right = new_width
            bottom = top + new_height
        
        # Crop and resize
        image = image.crop((left, top, right, bottom))
        image = image.resize(target_size, Image.LANCZOS)
        
        return image
    
    def generate_image(self, text: str, category: str, size_key: str = "twitter") -> str:
        """
        Generate an image based on text content and category.
        
        Args:
            text: Text content to base the image on
            category: Topic category
            size_key: Key for standard size ('twitter', 'square', or 'portrait')
            
        Returns:
            str: Path to the generated image file
        """
        try:
            # Determine image type based on category and content
            image_type = random.choice(["background", "chart"])
            
            if image_type == "chart" and category in ["Bitcoin", "Lightning Network", "Nostr", "Privacy", "Node Setup"]:
                # Create chart image
                base_image = self._create_chart_image(category)
            else:
                # Get background image
                base_image = self._get_background_image(category)
            
            # Resize image to target dimensions
            base_image = self._resize_image(base_image, size_key)
            
            # Add text overlay
            image_with_text = self._add_text_overlay(base_image, text, category)
            
            # Add branding
            final_image = self._add_branding(image_with_text)
            
            # Save image to temporary file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                final_image.save(tmp.name, format="JPEG", quality=95)
                output_path = tmp.name
            
            logger.info(f"Generated image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            
            # Create a simple fallback image
            try:
                fallback_image = self._generate_simple_background(category)
                fallback_image = self._resize_image(fallback_image, size_key)
                
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    fallback_image.save(tmp.name, format="JPEG", quality=90)
                    output_path = tmp.name
                
                logger.info(f"Fallback image saved to: {output_path}")
                return output_path
                
            except Exception as fallback_error:
                logger.error(f"Error creating fallback image: {str(fallback_error)}")
                return ""
    
    def save_image_to_file(self, image_path: str, output_dir: str, filename: str) -> str:
        """
        Save a generated image to a specific file.
        
        Args:
            image_path: Path to the temporary image file
            output_dir: Directory to save the image to
            filename: Base filename (without extension)
            
        Returns:
            str: Path to the saved image file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Determine output path
            output_path = os.path.join(output_dir, f"{filename}.jpg")
            
            # Copy the image
            image = Image.open(image_path)
            image.save(output_path, format="JPEG", quality=95)
            
            # Remove temporary file
            os.unlink(image_path)
            
            logger.info(f"Image saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving image to file: {str(e)}")
            return image_path  # Return original path if saving fails


# Example usage
if __name__ == "__main__":
    # This code will only run if the file is executed directly
    generator = ImageGenerator()
    
    # Example: Generate an image
    image_path = generator.generate_image(
        "Bitcoin is revolutionizing the financial system. Learn how it works and why it matters.",
        "Bitcoin"
    )
    
    print(f"Generated image: {image_path}")
