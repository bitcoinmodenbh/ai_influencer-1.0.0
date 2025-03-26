#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content Generation Module for AI Influencer System

This module handles the generation of content for the AI Influencer system, including:
- Topic selection based on configured preferences
- Text generation for posts about Bitcoin, Lightning Network, Nostr, etc.
- Hashtag generation (15 per post)
- Content formatting and optimization
"""

import os
import random
import json
import logging
from typing import Dict, List, Optional, Tuple, Union
import openai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("content_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ContentGenerator")

class ContentGenerator:
    """
    Class to handle content generation for the AI Influencer system.
    """
    
    # Define topic categories and specific topics
    TOPIC_CATEGORIES = {
        "Bitcoin": [
            "Bitcoin basics",
            "Bitcoin price analysis",
            "Bitcoin adoption",
            "Bitcoin mining",
            "Bitcoin security",
            "Bitcoin wallets",
            "Bitcoin history",
            "Bitcoin economics",
            "Bitcoin vs traditional finance",
            "Bitcoin regulation"
        ],
        "Lightning Network": [
            "Lightning Network basics",
            "Lightning Network nodes",
            "Lightning Network channels",
            "Lightning Network wallets",
            "Lightning Network payments",
            "Lightning Network apps",
            "Lightning Network security",
            "Lightning Network adoption",
            "Lightning Network vs on-chain",
            "Lightning Network development"
        ],
        "Nostr": [
            "Nostr basics",
            "Nostr relays",
            "Nostr clients",
            "Nostr identity",
            "Nostr vs centralized social media",
            "Nostr development",
            "Nostr adoption",
            "Nostr security",
            "Nostr integration",
            "Nostr communities"
        ],
        "Privacy": [
            "Online privacy basics",
            "Privacy tools",
            "Privacy best practices",
            "Privacy regulations",
            "Privacy vs convenience",
            "Privacy for Bitcoin users",
            "Privacy for Lightning users",
            "Privacy for Nostr users",
            "Privacy threats",
            "Privacy future"
        ],
        "Node Setup": [
            "Bitcoin node setup",
            "Lightning node setup",
            "Nostr relay setup",
            "Node hardware requirements",
            "Node software configuration",
            "Node maintenance",
            "Node security",
            "Node backups",
            "Node monitoring",
            "Node troubleshooting"
        ]
    }
    
    # Define hashtags for each category
    HASHTAGS = {
        "Bitcoin": [
            "#Bitcoin", "#BTC", "#Cryptocurrency", "#Crypto", "#DigitalGold",
            "#BitcoinHalving", "#HODL", "#Satoshi", "#Blockchain", "#BitcoinMining",
            "#CryptoTrading", "#BitcoinWallet", "#BitcoinSecurity", "#BitcoinAdoption",
            "#BitcoinEducation", "#SoundMoney", "#BitcoinDevelopment", "#BitcoinTech",
            "#Hyperbitcoinization", "#BTCPayServer", "#BitcoinNode", "#BitcoinCore",
            "#BitcoinPrice", "#BitcoinInvesting", "#BitcoinCommunity"
        ],
        "Lightning Network": [
            "#LightningNetwork", "#LN", "#Bitcoin", "#BTC", "#LightningNode",
            "#LightningWallet", "#LightningPayments", "#LightningApps", "#LightningDev",
            "#LightningTip", "#LightningChannels", "#LightningLabs", "#LightningLoop",
            "#LightningPool", "#LightningTerminal", "#LightningAddress", "#LNURL",
            "#LightningPrivacy", "#LightningAdoption", "#InstantPayments", "#Micropayments",
            "#LightningInvoice", "#LightningTorch", "#NodeRunners", "#LightningHackday"
        ],
        "Nostr": [
            "#Nostr", "#NostrRelay", "#NostrClient", "#NostrProtocol", "#NostrDev",
            "#NostrNIP", "#NostrEvents", "#NostrPubkey", "#NostrPrivkey", "#NostrZaps",
            "#NostrNotes", "#NostrDMs", "#NostrCommunity", "#NostrAdoption", "#NostrApps",
            "#DecentralizedSocial", "#NostrTools", "#NostrHackathon", "#NostrIntegration",
            "#NostrIdentity", "#NostrPrivacy", "#NostrSecurity", "#NostrUI", "#NostrUX",
            "#NostrStandards"
        ],
        "Privacy": [
            "#Privacy", "#OnlinePrivacy", "#DigitalPrivacy", "#PrivacyMatters", "#PrivacyTools",
            "#PrivacyByDesign", "#DataPrivacy", "#PrivacyRights", "#PrivacyProtection", "#OPSEC",
            "#PrivacyAdvocate", "#PrivacyAwareness", "#PrivacyTips", "#PrivacyTech", "#Encryption",
            "#EndToEndEncryption", "#VPN", "#Tor", "#PrivacyFocus", "#PrivacyFirst",
            "#PrivacyPolicy", "#PrivacySettings", "#PrivacyControl", "#PrivacyEducation",
            "#SecureMessaging"
        ],
        "Node Setup": [
            "#NodeSetup", "#BitcoinNode", "#LightningNode", "#NostrRelay", "#SelfHosted",
            "#NodeRunner", "#FullNode", "#NodeMaintenance", "#NodeSecurity", "#NodeBackup",
            "#NodeMonitoring", "#RaspberryPi", "#UmbrelNode", "#StartOSNode", "#MyNodeBTC",
            "#DIYNode", "#NodeHardware", "#NodeSoftware", "#NodeConfiguration", "#NodeUpgrade",
            "#NodeTroubleshooting", "#NodePerformance", "#NodeSync", "#NodeCommunity",
            "#SelfSovereignty"
        ]
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Content Generator.
        
        Args:
            api_key: OpenAI API key (optional)
        """
        # Load .env file if it exists
        load_dotenv()
        
        # Set OpenAI API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            logger.info("OpenAI API key set")
        else:
            logger.warning("No OpenAI API key provided")
        
        # Initialize topic history to track recently used topics
        self.topic_history = []
        
        # Load custom prompts if available
        self.custom_prompts = {}
        prompts_file = os.path.join(os.path.dirname(__file__), 'custom_prompts.json')
        if os.path.exists(prompts_file):
            try:
                with open(prompts_file, 'r') as f:
                    self.custom_prompts = json.load(f)
                logger.info("Loaded custom prompts from file")
            except Exception as e:
                logger.error(f"Error loading custom prompts: {str(e)}")
    
    def set_api_key(self, api_key: str) -> None:
        """
        Set the OpenAI API key.
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        openai.api_key = api_key
        logger.info("OpenAI API key updated")
    
    def select_topic(self, excluded_topics: Optional[List[str]] = None) -> Tuple[str, str]:
        """
        Select a topic for content generation, avoiding recently used topics.
        
        Args:
            excluded_topics: List of topics to exclude from selection
            
        Returns:
            tuple: (category, specific_topic)
        """
        excluded_topics = excluded_topics or []
        excluded_topics.extend(self.topic_history[-5:] if len(self.topic_history) > 5 else self.topic_history)
        
        # Select a random category
        categories = list(self.TOPIC_CATEGORIES.keys())
        category = random.choice(categories)
        
        # Select a specific topic from the category, avoiding recently used topics
        available_topics = [topic for topic in self.TOPIC_CATEGORIES[category] 
                           if f"{category}: {topic}" not in excluded_topics]
        
        # If all topics in this category were recently used, try another category
        if not available_topics:
            remaining_categories = [c for c in categories if c != category]
            if not remaining_categories:
                # If all topics have been used recently, reset history and select any topic
                self.topic_history = []
                category = random.choice(categories)
                specific_topic = random.choice(self.TOPIC_CATEGORIES[category])
            else:
                # Try another category
                category = random.choice(remaining_categories)
                specific_topic = random.choice(self.TOPIC_CATEGORIES[category])
        else:
            specific_topic = random.choice(available_topics)
        
        # Add to history
        self.topic_history.append(f"{category}: {specific_topic}")
        
        logger.info(f"Selected topic: {category} - {specific_topic}")
        return category, specific_topic
    
    def generate_hashtags(self, category: str, count: int = 15) -> List[str]:
        """
        Generate hashtags for a post based on the category.
        
        Args:
            category: The topic category
            count: Number of hashtags to generate
            
        Returns:
            list: List of hashtags
        """
        # Get hashtags for the specified category
        category_hashtags = self.HASHTAGS.get(category, [])
        
        # If we don't have enough hashtags in this category, add some from other categories
        if len(category_hashtags) < count:
            additional_hashtags = []
            for other_category, hashtags in self.HASHTAGS.items():
                if other_category != category:
                    additional_hashtags.extend(hashtags)
            
            # Shuffle and add additional hashtags
            random.shuffle(additional_hashtags)
            category_hashtags.extend(additional_hashtags)
        
        # Shuffle and select the required number of hashtags
        random.shuffle(category_hashtags)
        selected_hashtags = category_hashtags[:count]
        
        logger.info(f"Generated {count} hashtags for category: {category}")
        return selected_hashtags
    
    def generate_content(self, category: Optional[str] = None, 
                        specific_topic: Optional[str] = None,
                        max_length: int = 280) -> Dict:
        """
        Generate content for a post.
        
        Args:
            category: Topic category (optional)
            specific_topic: Specific topic (optional)
            max_length: Maximum length of the post content
            
        Returns:
            dict: Generated content including text, hashtags, and topic info
        """
        # Select a topic if not provided
        if not category or not specific_topic:
            category, specific_topic = self.select_topic()
        
        # Check if API key is set
        if not self.api_key:
            logger.error("Cannot generate content: No OpenAI API key provided")
            return {
                "success": False,
                "error": "No OpenAI API key provided",
                "category": category,
                "topic": specific_topic
            }
        
        try:
            # Get custom prompt if available, otherwise use default
            prompt_key = f"{category}_{specific_topic}".replace(" ", "_").lower()
            custom_prompt = self.custom_prompts.get(prompt_key)
            
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = f"Write a concise, informative tweet about {specific_topic} in the context of {category}. "
                prompt += f"The tweet should be educational, engaging, and under {max_length - 30} characters to leave room for hashtags. "
                prompt += "Include a thought-provoking question or call to action. Do not include hashtags in your response."
            
            # Generate content using OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in Bitcoin, Lightning Network, Nostr, and online privacy, creating educational content for social media."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            # Extract the generated text
            text = response.choices[0].message.content.strip()
            
            # Ensure text is within length limit
            if len(text) > max_length - 30:  # Leave room for hashtags
                text = text[:max_length - 33] + "..."
            
            # Generate hashtags
            hashtags = self.generate_hashtags(category)
            
            logger.info(f"Generated content for topic: {category} - {specific_topic}")
            
            return {
                "success": True,
                "text": text,
                "hashtags": hashtags,
                "category": category,
                "topic": specific_topic,
                "full_text_with_hashtags": f"{text}\n\n{' '.join(hashtags[:15])}"
            }
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "category": category,
                "topic": specific_topic
            }
    
    def generate_content_without_api(self, category: Optional[str] = None, 
                                   specific_topic: Optional[str] = None) -> Dict:
        """
        Generate content without using the OpenAI API (fallback method).
        
        Args:
            category: Topic category (optional)
            specific_topic: Specific topic (optional)
            
        Returns:
            dict: Generated content including text, hashtags, and topic info
        """
        # Select a topic if not provided
        if not category or not specific_topic:
            category, specific_topic = self.select_topic()
        
        # Template-based content generation
        templates = [
            "Exploring the world of {topic} today. What's your experience with it? #Bitcoin #Crypto",
            "Did you know? {topic} is changing how we think about digital sovereignty. Learn more!",
            "The future of {topic} looks promising. Here's why it matters for everyone in the {category} space.",
            "{topic} offers incredible possibilities for freedom and privacy. Are you taking advantage of it?",
            "Just set up a new {topic} configuration. Game-changer for my {category} experience!",
            "Thinking about {topic} and its implications for the future of {category}. Thoughts?",
            "Today's focus: {topic}. Essential knowledge for anyone interested in {category}.",
            "{topic} might be the most underrated aspect of {category}. Change my mind!",
            "The evolution of {topic} shows how far we've come in the {category} ecosystem.",
            "Security tip: Always consider {topic} when working with {category} technologies."
        ]
        
        # Select a random template and fill it
        template = random.choice(templates)
        text = template.format(topic=specific_topic, category=category)
        
        # Generate hashtags
        hashtags = self.generate_hashtags(category)
        
        logger.info(f"Generated template-based content for topic: {category} - {specific_topic}")
        
        return {
            "success": True,
            "text": text,
            "hashtags": hashtags,
            "category": category,
            "topic": specific_topic,
            "full_text_with_hashtags": f"{text}\n\n{' '.join(hashtags[:15])}"
        }
    
    def save_custom_prompt(self, category: str, specific_topic: str, prompt: str) -> bool:
        """
        Save a custom prompt for a specific topic.
        
        Args:
            category: Topic category
            specific_topic: Specific topic
            prompt: Custom prompt text
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            prompt_key = f"{category}_{specific_topic}".replace(" ", "_").lower()
            self.custom_prompts[prompt_key] = prompt
            
            # Save to file
            prompts_file = os.path.join(os.path.dirname(__file__), 'custom_prompts.json')
            with open(prompts_file, 'w') as f:
                json.dump(self.custom_prompts, f, indent=2)
            
            logger.info(f"Saved custom prompt for {category} - {specific_topic}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving custom prompt: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # This code will only run if the file is executed directly
    generator = ContentGenerator()
    
    # Example: Set API key manually
    # generator.set_api_key("your_openai_api_key")
    
    # Example: Generate content
    # content = generator.generate_content()
    # if content["success"]:
    #     print(f"Generated content: {content['full_text_with_hashtags']}")
    # else:
    #     print(f"Error: {content['error']}")
    
    # Example: Generate content without API
    content = generator.generate_content_without_api()
    print(f"Generated content: {content['full_text_with_hashtags']}")
