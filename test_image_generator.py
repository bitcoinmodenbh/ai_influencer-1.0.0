#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Image Generator Test Module

This module provides test cases for the image generation module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
from PIL import Image
from image_generator import ImageGenerator

class TestImageGenerator(unittest.TestCase):
    """Test cases for the ImageGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for assets
        self.temp_dir = tempfile.TemporaryDirectory()
        self.assets_dir = os.path.join(self.temp_dir.name, 'assets')
        
        # Create subdirectories
        os.makedirs(os.path.join(self.assets_dir, 'backgrounds'), exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, 'icons'), exist_ok=True)
        os.makedirs(os.path.join(self.assets_dir, 'fonts'), exist_ok=True)
        
        # Create a test background image
        bg_dir = os.path.join(self.assets_dir, 'backgrounds')
        test_bg = Image.new('RGB', (800, 600), color='blue')
        test_bg.save(os.path.join(bg_dir, 'bitcoin_test.jpg'))
        
        # Initialize generator with test assets directory
        self.generator = ImageGenerator(assets_dir=self.assets_dir)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_generate_simple_background(self):
        """Test generating a simple background."""
        # Generate background for Bitcoin category
        bg_image = self.generator._generate_simple_background("Bitcoin")
        
        # Verify the result
        self.assertIsInstance(bg_image, Image.Image)
        self.assertEqual(bg_image.size, self.generator.IMAGE_SIZES["twitter"])
        self.assertEqual(bg_image.mode, 'RGB')
    
    def test_resize_image(self):
        """Test image resizing functionality."""
        # Create a test image
        test_image = Image.new('RGB', (1000, 500), color='red')
        
        # Resize to Twitter dimensions
        resized = self.generator._resize_image(test_image, "twitter")
        
        # Verify the result
        self.assertEqual(resized.size, self.generator.IMAGE_SIZES["twitter"])
        
        # Test with different aspect ratio
        test_image2 = Image.new('RGB', (500, 1000), color='green')
        resized2 = self.generator._resize_image(test_image2, "square")
        
        # Verify the result
        self.assertEqual(resized2.size, self.generator.IMAGE_SIZES["square"])
    
    def test_add_text_overlay(self):
        """Test adding text overlay to an image."""
        # Create a test image
        test_image = Image.new('RGB', (1200, 675), color='black')
        
        # Add text overlay
        text = "This is a test message for Bitcoin enthusiasts."
        result = self.generator._add_text_overlay(test_image, text, "Bitcoin")
        
        # Verify the result
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (1200, 675))
        self.assertEqual(result.mode, 'RGB')
    
    def test_add_branding(self):
        """Test adding branding to an image."""
        # Create a test image
        test_image = Image.new('RGB', (1200, 675), color='black')
        
        # Add branding
        result = self.generator._add_branding(test_image)
        
        # Verify the result
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (1200, 675))
    
    @patch('matplotlib.pyplot.savefig')
    def test_create_chart_image(self, mock_savefig):
        """Test chart image creation."""
        # Mock the savefig method to avoid actual file operations
        mock_savefig.side_effect = lambda buf, format, dpi: None
        
        # Create a BytesIO object that returns a valid image when opened
        with patch('PIL.Image.open') as mock_open:
            mock_image = MagicMock()
            mock_image.size = (1200, 675)
            mock_open.return_value = mock_image
            
            # Test chart creation for each category
            for category in ["Bitcoin", "Lightning Network", "Nostr", "Privacy", "Node Setup"]:
                result = self.generator._create_chart_image(category)
                self.assertEqual(result, mock_image)
    
    def test_generate_image(self):
        """Test the main image generation method."""
        # Mock internal methods to avoid actual image operations
        with patch.object(self.generator, '_get_background_image') as mock_bg, \
             patch.object(self.generator, '_resize_image') as mock_resize, \
             patch.object(self.generator, '_add_text_overlay') as mock_text, \
             patch.object(self.generator, '_add_branding') as mock_brand:
            
            # Set up mocks
            mock_bg.return_value = Image.new('RGB', (800, 600), color='blue')
            mock_resize.return_value = Image.new('RGB', (1200, 675), color='blue')
            mock_text.return_value = Image.new('RGB', (1200, 675), color='blue')
            mock_brand.return_value = Image.new('RGB', (1200, 675), color='blue')
            
            # Generate image
            text = "Test message about Bitcoin"
            result_path = self.generator.generate_image(text, "Bitcoin")
            
            # Verify the result
            self.assertTrue(os.path.exists(result_path))
            self.assertTrue(result_path.endswith('.jpg'))
            
            # Clean up
            if os.path.exists(result_path):
                os.unlink(result_path)
    
    def test_save_image_to_file(self):
        """Test saving an image to a specific file."""
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            test_image = Image.new('RGB', (100, 100), color='red')
            test_image.save(tmp.name)
            temp_path = tmp.name
        
        # Save to a specific location
        output_dir = os.path.join(self.temp_dir.name, 'output')
        result_path = self.generator.save_image_to_file(temp_path, output_dir, "test_image")
        
        # Verify the result
        self.assertTrue(os.path.exists(result_path))
        self.assertTrue(result_path.endswith('test_image.jpg'))
        self.assertEqual(os.path.dirname(result_path), output_dir)
        
        # Clean up
        if os.path.exists(result_path):
            os.unlink(result_path)


if __name__ == '__main__':
    unittest.main()
