#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integration Test Module for AI Influencer System

This module provides integration tests for the AI Influencer system.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import json

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twitter_api import TwitterAPI
from content_generator import ContentGenerator
from image_generator import ImageGenerator
from gui import AIInfluencerGUI, PostingWorker, ScheduleWorker

class TestIntegration(unittest.TestCase):
    """Integration tests for the AI Influencer system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = self.temp_dir.name
        
        # Create mock components
        self.twitter_api = MagicMock(spec=TwitterAPI)
        self.content_generator = MagicMock(spec=ContentGenerator)
        self.image_generator = MagicMock(spec=ImageGenerator)
        
        # Set up mock returns
        self.twitter_api.authenticate.return_value = True
        self.twitter_api.post_tweet.return_value = "12345"
        
        self.content_generator.generate_content.return_value = {
            "success": True,
            "text": "Test tweet about Bitcoin",
            "hashtags": ["#Bitcoin", "#Crypto", "#BTC"],
            "category": "Bitcoin",
            "topic": "Bitcoin basics",
            "full_text_with_hashtags": "Test tweet about Bitcoin\n\n#Bitcoin #Crypto #BTC"
        }
        
        self.image_generator.generate_image.return_value = os.path.join(self.data_dir, "test_image.jpg")
        
        # Create test image file
        with open(os.path.join(self.data_dir, "test_image.jpg"), "w") as f:
            f.write("test image content")
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_posting_worker(self):
        """Test the posting worker integration."""
        # Create posting worker
        worker = PostingWorker(
            self.twitter_api,
            self.content_generator,
            self.image_generator
        )
        
        # Mock signals
        worker.status_update = MagicMock()
        worker.post_complete = MagicMock()
        worker.post_error = MagicMock()
        
        # Run the worker
        worker.run()
        
        # Verify interactions
        self.content_generator.generate_content.assert_called_once()
        self.image_generator.generate_image.assert_called_once_with(
            "Test tweet about Bitcoin", 
            "Bitcoin"
        )
        self.twitter_api.post_tweet.assert_called_once_with(
            "Test tweet about Bitcoin\n\n#Bitcoin #Crypto #BTC",
            os.path.join(self.data_dir, "test_image.jpg")
        )
        
        # Verify signals
        worker.status_update.assert_called()
        worker.post_complete.assert_called_once()
        worker.post_error.assert_not_called()
    
    def test_posting_worker_content_error(self):
        """Test the posting worker with content generation error."""
        # Set up content generator to return error
        self.content_generator.generate_content.return_value = {
            "success": False,
            "error": "API error",
            "category": "Bitcoin",
            "topic": "Bitcoin basics"
        }
        
        # Set up fallback method
        self.content_generator.generate_content_without_api.return_value = {
            "success": True,
            "text": "Fallback tweet about Bitcoin",
            "hashtags": ["#Bitcoin", "#Crypto", "#BTC"],
            "category": "Bitcoin",
            "topic": "Bitcoin basics",
            "full_text_with_hashtags": "Fallback tweet about Bitcoin\n\n#Bitcoin #Crypto #BTC"
        }
        
        # Create posting worker
        worker = PostingWorker(
            self.twitter_api,
            self.content_generator,
            self.image_generator
        )
        
        # Mock signals
        worker.status_update = MagicMock()
        worker.post_complete = MagicMock()
        worker.post_error = MagicMock()
        
        # Run the worker
        worker.run()
        
        # Verify interactions
        self.content_generator.generate_content.assert_called_once()
        self.content_generator.generate_content_without_api.assert_called_once()
        self.image_generator.generate_image.assert_called_once_with(
            "Fallback tweet about Bitcoin", 
            "Bitcoin"
        )
        self.twitter_api.post_tweet.assert_called_once()
        
        # Verify signals
        worker.status_update.assert_called()
        worker.post_complete.assert_called_once()
        worker.post_error.assert_not_called()
    
    def test_posting_worker_image_error(self):
        """Test the posting worker with image generation error."""
        # Set up image generator to return error
        self.image_generator.generate_image.return_value = ""
        
        # Create posting worker
        worker = PostingWorker(
            self.twitter_api,
            self.content_generator,
            self.image_generator
        )
        
        # Mock signals
        worker.status_update = MagicMock()
        worker.post_complete = MagicMock()
        worker.post_error = MagicMock()
        
        # Run the worker
        worker.run()
        
        # Verify interactions
        self.content_generator.generate_content.assert_called_once()
        self.image_generator.generate_image.assert_called_once()
        self.twitter_api.post_tweet.assert_not_called()
        
        # Verify signals
        worker.status_update.assert_called()
        worker.post_complete.assert_not_called()
        worker.post_error.assert_called_once()
    
    def test_posting_worker_twitter_error(self):
        """Test the posting worker with Twitter API error."""
        # Set up Twitter API to return error
        self.twitter_api.post_tweet.return_value = None
        
        # Create posting worker
        worker = PostingWorker(
            self.twitter_api,
            self.content_generator,
            self.image_generator
        )
        
        # Mock signals
        worker.status_update = MagicMock()
        worker.post_complete = MagicMock()
        worker.post_error = MagicMock()
        
        # Run the worker
        worker.run()
        
        # Verify interactions
        self.content_generator.generate_content.assert_called_once()
        self.image_generator.generate_image.assert_called_once()
        self.twitter_api.post_tweet.assert_called_once()
        
        # Verify signals
        worker.status_update.assert_called()
        worker.post_complete.assert_not_called()
        worker.post_error.assert_called_once()
    
    @patch('PyQt5.QtCore.QThread.msleep')
    def test_schedule_worker(self, mock_sleep):
        """Test the schedule worker."""
        # Create schedule worker with short interval for testing
        worker = ScheduleWorker(interval_hours=0.001)  # Almost immediate
        
        # Mock signals
        worker.schedule_update = MagicMock()
        worker.trigger_post = MagicMock()
        
        # Set up to run briefly then stop
        def stop_after_trigger(*args, **kwargs):
            worker.running = False
        
        worker.trigger_post.connect(stop_after_trigger)
        
        # Run the worker
        worker.run()
        
        # Verify signals
        worker.schedule_update.assert_called()
        worker.trigger_post.assert_called_once()
    
    def test_content_image_integration(self):
        """Test integration between content and image generation."""
        # Create real instances for this test
        content_gen = ContentGenerator()
        image_gen = ImageGenerator()
        
        # Generate content without API
        content = content_gen.generate_content_without_api()
        
        # Verify content
        self.assertTrue(content["success"])
        self.assertIn("category", content)
        self.assertIn("topic", content)
        self.assertIn("text", content)
        self.assertIn("hashtags", content)
        self.assertEqual(len(content["hashtags"]), 15)
        
        # Generate image from content
        image_path = image_gen.generate_image(content["text"], content["category"])
        
        # Verify image
        self.assertTrue(os.path.exists(image_path))
        self.assertTrue(image_path.endswith('.jpg'))
        
        # Clean up
        if os.path.exists(image_path):
            os.unlink(image_path)


if __name__ == '__main__':
    unittest.main()
