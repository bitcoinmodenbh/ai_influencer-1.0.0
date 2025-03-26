#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content Generator Test Module

This module provides test cases for the content generation module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import json
import tempfile
from content_generator import ContentGenerator

class TestContentGenerator(unittest.TestCase):
    """Test cases for the ContentGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = ContentGenerator()
    
    def test_select_topic(self):
        """Test topic selection functionality."""
        # Test basic topic selection
        category, specific_topic = self.generator.select_topic()
        self.assertIn(category, self.generator.TOPIC_CATEGORIES.keys())
        self.assertIn(specific_topic, self.generator.TOPIC_CATEGORIES[category])
        
        # Test topic history tracking
        self.assertEqual(len(self.generator.topic_history), 1)
        self.assertEqual(self.generator.topic_history[0], f"{category}: {specific_topic}")
        
        # Test exclusion of topics
        excluded_topic = f"{category}: {specific_topic}"
        new_category, new_specific_topic = self.generator.select_topic([excluded_topic])
        self.assertNotEqual(f"{new_category}: {new_specific_topic}", excluded_topic)
    
    def test_generate_hashtags(self):
        """Test hashtag generation."""
        # Test generating hashtags for a specific category
        category = "Bitcoin"
        hashtags = self.generator.generate_hashtags(category, count=15)
        
        # Verify we got the right number of hashtags
        self.assertEqual(len(hashtags), 15)
        
        # Verify all hashtags start with #
        for hashtag in hashtags:
            self.assertTrue(hashtag.startswith('#'))
        
        # Test with invalid category
        invalid_hashtags = self.generator.generate_hashtags("InvalidCategory", count=5)
        self.assertEqual(len(invalid_hashtags), 5)
    
    @patch('openai.ChatCompletion.create')
    def test_generate_content_with_api(self, mock_create):
        """Test content generation with OpenAI API."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is a test tweet about Bitcoin basics."
        mock_create.return_value = mock_response
        
        # Set API key
        self.generator.set_api_key("test_api_key")
        
        # Generate content
        content = self.generator.generate_content(category="Bitcoin", specific_topic="Bitcoin basics")
        
        # Verify the result
        self.assertTrue(content["success"])
        self.assertEqual(content["text"], "This is a test tweet about Bitcoin basics.")
        self.assertEqual(content["category"], "Bitcoin")
        self.assertEqual(content["topic"], "Bitcoin basics")
        self.assertEqual(len(content["hashtags"]), 15)
        self.assertIn(content["text"], content["full_text_with_hashtags"])
    
    def test_generate_content_without_api(self):
        """Test content generation without OpenAI API."""
        # Generate content without API
        content = self.generator.generate_content_without_api(category="Lightning Network", specific_topic="Lightning Network nodes")
        
        # Verify the result
        self.assertTrue(content["success"])
        self.assertEqual(content["category"], "Lightning Network")
        self.assertEqual(content["topic"], "Lightning Network nodes")
        self.assertEqual(len(content["hashtags"]), 15)
        self.assertIn(content["text"], content["full_text_with_hashtags"])
        self.assertIn("Lightning Network nodes", content["text"])
    
    @patch('openai.ChatCompletion.create')
    def test_generate_content_api_error(self, mock_create):
        """Test content generation with API error."""
        # Set up mock to raise an exception
        mock_create.side_effect = Exception("API Error")
        
        # Set API key
        self.generator.set_api_key("test_api_key")
        
        # Generate content
        content = self.generator.generate_content(category="Nostr", specific_topic="Nostr relays")
        
        # Verify the result
        self.assertFalse(content["success"])
        self.assertEqual(content["category"], "Nostr")
        self.assertEqual(content["topic"], "Nostr relays")
        self.assertIn("API Error", content["error"])
    
    def test_save_custom_prompt(self):
        """Test saving custom prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Patch the __file__ attribute to use the temp directory
            original_dirname = os.path.dirname
            try:
                os.path.dirname = MagicMock(return_value=temp_dir)
                
                # Save a custom prompt
                result = self.generator.save_custom_prompt(
                    category="Bitcoin", 
                    specific_topic="Bitcoin security",
                    prompt="Write about Bitcoin security best practices."
                )
                
                # Verify the result
                self.assertTrue(result)
                
                # Check if the file was created
                prompts_file = os.path.join(temp_dir, 'custom_prompts.json')
                self.assertTrue(os.path.exists(prompts_file))
                
                # Verify the content
                with open(prompts_file, 'r') as f:
                    prompts = json.load(f)
                
                self.assertIn("bitcoin_bitcoin_security", prompts)
                self.assertEqual(prompts["bitcoin_bitcoin_security"], "Write about Bitcoin security best practices.")
                
            finally:
                os.path.dirname = original_dirname


if __name__ == '__main__':
    unittest.main()
