#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Twitter API Integration Test Module

This module provides test cases for the Twitter API integration module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import json
import tempfile
from twitter_api import TwitterAPI

class TestTwitterAPI(unittest.TestCase):
    """Test cases for the TwitterAPI class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_credentials = {
            'api_key': 'test_api_key',
            'api_secret': 'test_api_secret',
            'access_token': 'test_access_token',
            'access_token_secret': 'test_access_token_secret'
        }
        
        # Create a temporary credentials file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.credentials_file = os.path.join(self.temp_dir.name, 'credentials.json')
        with open(self.credentials_file, 'w') as f:
            json.dump(self.test_credentials, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_load_credentials_from_file(self):
        """Test loading credentials from a file."""
        twitter = TwitterAPI(credentials_file=self.credentials_file)
        self.assertEqual(twitter.api_key, self.test_credentials['api_key'])
        self.assertEqual(twitter.api_secret, self.test_credentials['api_secret'])
        self.assertEqual(twitter.access_token, self.test_credentials['access_token'])
        self.assertEqual(twitter.access_token_secret, self.test_credentials['access_token_secret'])
    
    @patch.dict(os.environ, {
        'TWITTER_API_KEY': 'env_api_key',
        'TWITTER_API_SECRET': 'env_api_secret',
        'TWITTER_ACCESS_TOKEN': 'env_access_token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'env_access_token_secret'
    })
    def test_load_credentials_from_env(self):
        """Test loading credentials from environment variables."""
        twitter = TwitterAPI()
        self.assertEqual(twitter.api_key, 'env_api_key')
        self.assertEqual(twitter.api_secret, 'env_api_secret')
        self.assertEqual(twitter.access_token, 'env_access_token')
        self.assertEqual(twitter.access_token_secret, 'env_access_token_secret')
    
    def test_set_credentials_manually(self):
        """Test setting credentials manually."""
        twitter = TwitterAPI()
        twitter.set_credentials(
            api_key='manual_api_key',
            api_secret='manual_api_secret',
            access_token='manual_access_token',
            access_token_secret='manual_access_token_secret'
        )
        self.assertEqual(twitter.api_key, 'manual_api_key')
        self.assertEqual(twitter.api_secret, 'manual_api_secret')
        self.assertEqual(twitter.access_token, 'manual_access_token')
        self.assertEqual(twitter.access_token_secret, 'manual_access_token_secret')
    
    def test_save_credentials(self):
        """Test saving credentials to a file."""
        twitter = TwitterAPI()
        twitter.set_credentials(
            api_key='save_api_key',
            api_secret='save_api_secret',
            access_token='save_access_token',
            access_token_secret='save_access_token_secret'
        )
        
        save_file = os.path.join(self.temp_dir.name, 'saved_credentials.json')
        result = twitter.save_credentials(save_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(save_file))
        
        with open(save_file, 'r') as f:
            saved_credentials = json.load(f)
        
        self.assertEqual(saved_credentials['api_key'], 'save_api_key')
        self.assertEqual(saved_credentials['api_secret'], 'save_api_secret')
        self.assertEqual(saved_credentials['access_token'], 'save_access_token')
        self.assertEqual(saved_credentials['access_token_secret'], 'save_access_token_secret')
    
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    @patch('tweepy.Client')
    def test_authenticate_success(self, mock_client, mock_api, mock_auth):
        """Test successful authentication."""
        # Set up mocks
        mock_auth_instance = MagicMock()
        mock_auth.return_value = mock_auth_instance
        
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Create TwitterAPI instance and authenticate
        twitter = TwitterAPI(credentials_file=self.credentials_file)
        result = twitter.authenticate()
        
        # Assertions
        self.assertTrue(result)
        self.assertTrue(twitter.authenticated)
        mock_auth.assert_called_once_with(
            self.test_credentials['api_key'],
            self.test_credentials['api_secret'],
            self.test_credentials['access_token'],
            self.test_credentials['access_token_secret']
        )
        mock_api.assert_called_once_with(mock_auth_instance)
        mock_client.assert_called_once()
    
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    def test_authenticate_failure(self, mock_api, mock_auth):
        """Test authentication failure."""
        # Set up mocks
        mock_auth_instance = MagicMock()
        mock_auth.return_value = mock_auth_instance
        
        mock_api_instance = MagicMock()
        mock_api_instance.verify_credentials.side_effect = Exception("Authentication failed")
        mock_api.return_value = mock_api_instance
        
        # Create TwitterAPI instance and authenticate
        twitter = TwitterAPI(credentials_file=self.credentials_file)
        result = twitter.authenticate()
        
        # Assertions
        self.assertFalse(result)
        self.assertFalse(twitter.authenticated)
    
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    @patch('tweepy.Client')
    def test_post_tweet_text_only(self, mock_client, mock_api, mock_auth):
        """Test posting a tweet with text only."""
        # Set up mocks
        mock_auth_instance = MagicMock()
        mock_auth.return_value = mock_auth_instance
        
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        
        mock_client_instance = MagicMock()
        mock_client_instance.create_tweet.return_value = MagicMock(data={'id': '12345'})
        mock_client.return_value = mock_client_instance
        
        # Create TwitterAPI instance and post tweet
        twitter = TwitterAPI(credentials_file=self.credentials_file)
        twitter.authenticate()
        tweet_id = twitter.post_tweet("Test tweet")
        
        # Assertions
        self.assertEqual(tweet_id, '12345')
        mock_client_instance.create_tweet.assert_called_once_with(text="Test tweet")
    
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    @patch('tweepy.Client')
    @patch('os.path.exists')
    def test_post_tweet_with_image(self, mock_exists, mock_client, mock_api, mock_auth):
        """Test posting a tweet with an image."""
        # Set up mocks
        mock_auth_instance = MagicMock()
        mock_auth.return_value = mock_auth_instance
        
        mock_media = MagicMock()
        mock_media.media_id = '67890'
        
        mock_api_instance = MagicMock()
        mock_api_instance.media_upload.return_value = mock_media
        mock_api.return_value = mock_api_instance
        
        mock_client_instance = MagicMock()
        mock_client_instance.create_tweet.return_value = MagicMock(data={'id': '12345'})
        mock_client.return_value = mock_client_instance
        
        mock_exists.return_value = True
        
        # Create TwitterAPI instance and post tweet with image
        twitter = TwitterAPI(credentials_file=self.credentials_file)
        twitter.authenticate()
        tweet_id = twitter.post_tweet("Test tweet with image", image_path="test_image.jpg")
        
        # Assertions
        self.assertEqual(tweet_id, '12345')
        mock_api_instance.media_upload.assert_called_once_with("test_image.jpg")
        mock_client_instance.create_tweet.assert_called_once_with(text="Test tweet with image", media_ids=['67890'])
    
    @patch('tweepy.OAuth1UserHandler')
    @patch('tweepy.API')
    def test_get_user_info(self, mock_api, mock_auth):
        """Test getting user information."""
        # Set up mocks
        mock_auth_instance = MagicMock()
        mock_auth.return_value = mock_auth_instance
        
        mock_user = MagicMock()
        mock_user.id = 123456
        mock_user.screen_name = 'test_user'
        mock_user.name = 'Test User'
        mock_user.description = 'Test description'
        mock_user.followers_count = 100
        mock_user.friends_count = 50
        mock_user.statuses_count = 200
        mock_user.profile_image_url_https = 'https://example.com/image.jpg'
        
        mock_api_instance = MagicMock()
        mock_api_instance.verify_credentials.return_value = mock_user
        mock_api.return_value = mock_api_instance
        
        # Create TwitterAPI instance and get user info
        twitter = TwitterAPI(credentials_file=self.credentials_file)
        twitter.authenticate()
        user_info = twitter.get_user_info()
        
        # Assertions
        self.assertEqual(user_info['id'], 123456)
        self.assertEqual(user_info['screen_name'], 'test_user')
        self.assertEqual(user_info['name'], 'Test User')
        self.assertEqual(user_info['description'], 'Test description')
        self.assertEqual(user_info['followers_count'], 100)
        self.assertEqual(user_info['friends_count'], 50)
        self.assertEqual(user_info['statuses_count'], 200)
        self.assertEqual(user_info['profile_image_url'], 'https://example.com/image.jpg')


if __name__ == '__main__':
    unittest.main()
