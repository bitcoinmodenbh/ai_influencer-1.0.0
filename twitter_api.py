#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Twitter API Integration Module for AI Influencer System

This module handles all interactions with the Twitter API, including:
- Authentication with API credentials
- Posting text content
- Uploading and attaching images
- Handling API rate limits and errors
- Retrieving account information and post history
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Union
import tweepy
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("twitter_api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TwitterAPI")

class TwitterAPI:
    """
    Class to handle all Twitter API interactions for the AI Influencer system.
    """
    
    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize the Twitter API client.
        
        Args:
            credentials_file: Path to the credentials file (optional)
        """
        self.api = None
        self.client = None
        self.authenticated = False
        
        # Try to load credentials from file or environment variables
        if credentials_file and os.path.exists(credentials_file):
            self._load_credentials_from_file(credentials_file)
        else:
            self._load_credentials_from_env()
    
    def _load_credentials_from_file(self, credentials_file: str) -> None:
        """
        Load API credentials from a JSON file.
        
        Args:
            credentials_file: Path to the credentials JSON file
        """
        try:
            with open(credentials_file, 'r') as f:
                credentials = json.load(f)
                
            self.api_key = credentials.get('api_key')
            self.api_secret = credentials.get('api_secret')
            self.access_token = credentials.get('access_token')
            self.access_token_secret = credentials.get('access_token_secret')
            
            logger.info("Credentials loaded from file")
        except Exception as e:
            logger.error(f"Error loading credentials from file: {str(e)}")
            raise
    
    def _load_credentials_from_env(self) -> None:
        """
        Load API credentials from environment variables.
        """
        # Load .env file if it exists
        load_dotenv()
        
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            logger.info("Credentials loaded from environment variables")
        else:
            logger.warning("Some credentials are missing from environment variables")
    
    def authenticate(self) -> bool:
        """
        Authenticate with the Twitter API using the loaded credentials.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        try:
            # Check if credentials are available
            if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                logger.error("Missing credentials for Twitter API authentication")
                return False
            
            # Set up authentication with tweepy
            auth = tweepy.OAuth1UserHandler(
                self.api_key, 
                self.api_secret,
                self.access_token,
                self.access_token_secret
            )
            
            # Create API and Client objects
            self.api = tweepy.API(auth)
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            
            # Verify credentials
            self.api.verify_credentials()
            self.authenticated = True
            logger.info("Successfully authenticated with Twitter API")
            return True
            
        except tweepy.TweepyException as e:
            logger.error(f"Authentication error: {str(e)}")
            self.authenticated = False
            return False
    
    def set_credentials(self, api_key: str, api_secret: str, 
                       access_token: str, access_token_secret: str) -> None:
        """
        Set API credentials manually.
        
        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: Twitter access token
            access_token_secret: Twitter access token secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        logger.info("Credentials set manually")
    
    def save_credentials(self, credentials_file: str) -> bool:
        """
        Save the current credentials to a file.
        
        Args:
            credentials_file: Path to save the credentials
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            credentials = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'access_token': self.access_token,
                'access_token_secret': self.access_token_secret
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(credentials_file), exist_ok=True)
            
            with open(credentials_file, 'w') as f:
                json.dump(credentials, f)
            
            logger.info(f"Credentials saved to {credentials_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            return False
    
    def post_tweet(self, text: str, image_path: Optional[str] = None) -> Optional[str]:
        """
        Post a tweet with optional image attachment.
        
        Args:
            text: The text content of the tweet
            image_path: Optional path to an image file to attach
            
        Returns:
            str: ID of the posted tweet if successful, None otherwise
        """
        if not self.authenticated:
            if not self.authenticate():
                logger.error("Cannot post tweet: Not authenticated")
                return None
        
        try:
            # Handle image upload if provided
            media_ids = []
            if image_path and os.path.exists(image_path):
                media = self.api.media_upload(image_path)
                media_ids.append(media.media_id)
                logger.info(f"Uploaded image: {image_path}")
            
            # Post the tweet
            if media_ids:
                response = self.client.create_tweet(text=text, media_ids=media_ids)
            else:
                response = self.client.create_tweet(text=text)
            
            tweet_id = response.data['id']
            logger.info(f"Successfully posted tweet with ID: {tweet_id}")
            return tweet_id
            
        except tweepy.TweepyException as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return None
    
    def get_user_info(self) -> Optional[Dict]:
        """
        Get information about the authenticated user.
        
        Returns:
            dict: User information if successful, None otherwise
        """
        if not self.authenticated:
            if not self.authenticate():
                logger.error("Cannot get user info: Not authenticated")
                return None
        
        try:
            user = self.api.verify_credentials()
            user_info = {
                'id': user.id,
                'screen_name': user.screen_name,
                'name': user.name,
                'description': user.description,
                'followers_count': user.followers_count,
                'friends_count': user.friends_count,
                'statuses_count': user.statuses_count,
                'profile_image_url': user.profile_image_url_https
            }
            return user_info
            
        except tweepy.TweepyException as e:
            logger.error(f"Error getting user info: {str(e)}")
            return None
    
    def get_user_tweets(self, count: int = 10) -> Optional[List[Dict]]:
        """
        Get recent tweets from the authenticated user.
        
        Args:
            count: Number of tweets to retrieve
            
        Returns:
            list: List of tweet dictionaries if successful, None otherwise
        """
        if not self.authenticated:
            if not self.authenticate():
                logger.error("Cannot get user tweets: Not authenticated")
                return None
        
        try:
            tweets = self.api.user_timeline(count=count)
            
            tweet_list = []
            for tweet in tweets:
                tweet_data = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                    'has_media': hasattr(tweet, 'entities') and 'media' in tweet.entities
                }
                tweet_list.append(tweet_data)
            
            return tweet_list
            
        except tweepy.TweepyException as e:
            logger.error(f"Error getting user tweets: {str(e)}")
            return None
    
    def search_tweets(self, query: str, count: int = 20) -> Optional[List[Dict]]:
        """
        Search for tweets matching a query.
        
        Args:
            query: Search query
            count: Number of tweets to retrieve
            
        Returns:
            list: List of tweet dictionaries if successful, None otherwise
        """
        if not self.authenticated:
            if not self.authenticate():
                logger.error("Cannot search tweets: Not authenticated")
                return None
        
        try:
            tweets = self.api.search_tweets(q=query, count=count)
            
            tweet_list = []
            for tweet in tweets:
                tweet_data = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'user': {
                        'id': tweet.user.id,
                        'screen_name': tweet.user.screen_name,
                        'name': tweet.user.name
                    },
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count
                }
                tweet_list.append(tweet_data)
            
            return tweet_list
            
        except tweepy.TweepyException as e:
            logger.error(f"Error searching tweets: {str(e)}")
            return None
    
    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet by ID.
        
        Args:
            tweet_id: ID of the tweet to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.authenticated:
            if not self.authenticate():
                logger.error("Cannot delete tweet: Not authenticated")
                return False
        
        try:
            self.client.delete_tweet(id=tweet_id)
            logger.info(f"Successfully deleted tweet with ID: {tweet_id}")
            return True
            
        except tweepy.TweepyException as e:
            logger.error(f"Error deleting tweet: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # This code will only run if the file is executed directly
    twitter = TwitterAPI()
    
    # Example: Set credentials manually
    # twitter.set_credentials(
    #     api_key="YOUR_API_KEY",
    #     api_secret="YOUR_API_SECRET",
    #     access_token="YOUR_ACCESS_TOKEN",
    #     access_token_secret="YOUR_ACCESS_TOKEN_SECRET"
    # )
    
    # Example: Authenticate and post a tweet
    # if twitter.authenticate():
    #     tweet_id = twitter.post_tweet("Hello, world! This is a test tweet from the AI Influencer system.")
    #     if tweet_id:
    #         print(f"Tweet posted successfully with ID: {tweet_id}")
