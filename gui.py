#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Graphical User Interface for AI Influencer System

This module provides a PyQt5-based GUI for the AI Influencer system, including:
- API credential management
- Posting status monitoring
- Tweet history viewing
- Configuration settings
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Optional, Tuple, Union
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, 
                           QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
                           QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
                           QCheckBox, QSpinBox, QTableWidget, QTableWidgetItem,
                           QHeaderView, QFileDialog, QMessageBox, QProgressBar,
                           QGroupBox, QScrollArea, QFrame, QSplitter, QStatusBar)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from dotenv import load_dotenv

# Import other modules
from twitter_api import TwitterAPI
from content_generator import ContentGenerator
from image_generator import ImageGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gui.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GUI")

class PostingWorker(QThread):
    """Worker thread for handling posting operations."""
    
    # Define signals
    status_update = pyqtSignal(str)
    post_complete = pyqtSignal(dict)
    post_error = pyqtSignal(str)
    
    def __init__(self, twitter_api: TwitterAPI, content_generator: ContentGenerator, 
                image_generator: ImageGenerator):
        """
        Initialize the posting worker.
        
        Args:
            twitter_api: TwitterAPI instance
            content_generator: ContentGenerator instance
            image_generator: ImageGenerator instance
        """
        super().__init__()
        self.twitter_api = twitter_api
        self.content_generator = content_generator
        self.image_generator = image_generator
        self.running = False
    
    def run(self):
        """Run the posting process."""
        self.running = True
        
        try:
            # Generate content
            self.status_update.emit("Generating content...")
            content = self.content_generator.generate_content()
            
            if not content["success"]:
                # Try fallback method
                self.status_update.emit("Using fallback content generation...")
                content = self.content_generator.generate_content_without_api()
            
            # Generate image
            self.status_update.emit("Generating image...")
            image_path = self.image_generator.generate_image(
                content["text"], 
                content["category"]
            )
            
            if not image_path:
                self.post_error.emit("Failed to generate image")
                return
            
            # Post to Twitter
            self.status_update.emit("Posting to Twitter...")
            tweet_id = self.twitter_api.post_tweet(
                content["full_text_with_hashtags"],
                image_path
            )
            
            if not tweet_id:
                self.post_error.emit("Failed to post tweet")
                return
            
            # Create result
            result = {
                "tweet_id": tweet_id,
                "text": content["text"],
                "hashtags": content["hashtags"],
                "category": content["category"],
                "topic": content["topic"],
                "image_path": image_path,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Emit completion signal
            self.post_complete.emit(result)
            
        except Exception as e:
            logger.error(f"Error in posting worker: {str(e)}")
            self.post_error.emit(f"Error: {str(e)}")
        
        finally:
            self.running = False
    
    def stop(self):
        """Stop the worker."""
        self.running = False
        self.wait()


class ScheduleWorker(QThread):
    """Worker thread for handling scheduled posting."""
    
    # Define signals
    schedule_update = pyqtSignal(str)
    trigger_post = pyqtSignal()
    
    def __init__(self, interval_hours: int = 24):
        """
        Initialize the schedule worker.
        
        Args:
            interval_hours: Hours between posts
        """
        super().__init__()
        self.interval_hours = interval_hours
        self.running = False
        self.next_post_time = None
    
    def run(self):
        """Run the scheduling process."""
        self.running = True
        self.next_post_time = datetime.datetime.now() + datetime.timedelta(hours=self.interval_hours)
        
        while self.running:
            # Calculate time until next post
            now = datetime.datetime.now()
            time_diff = self.next_post_time - now
            
            # Update status
            hours, remainder = divmod(time_diff.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.schedule_update.emit(f"Next post in: {time_str}")
            
            # Check if it's time to post
            if now >= self.next_post_time:
                self.trigger_post.emit()
                self.next_post_time = now + datetime.timedelta(hours=self.interval_hours)
            
            # Sleep for a short time
            self.msleep(1000)  # 1 second
    
    def stop(self):
        """Stop the worker."""
        self.running = False
        self.wait()
    
    def set_interval(self, hours: int):
        """
        Set the posting interval.
        
        Args:
            hours: Hours between posts
        """
        self.interval_hours = hours
        self.next_post_time = datetime.datetime.now() + datetime.timedelta(hours=self.interval_hours)


class AIInfluencerGUI(QMainWindow):
    """Main GUI window for the AI Influencer system."""
    
    def __init__(self):
        """Initialize the GUI."""
        super().__init__()
        
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.twitter_api = TwitterAPI()
        self.content_generator = ContentGenerator()
        self.image_generator = ImageGenerator()
        
        # Initialize workers
        self.posting_worker = PostingWorker(
            self.twitter_api,
            self.content_generator,
            self.image_generator
        )
        self.schedule_worker = ScheduleWorker()
        
        # Connect worker signals
        self.posting_worker.status_update.connect(self.update_status)
        self.posting_worker.post_complete.connect(self.handle_post_complete)
        self.posting_worker.post_error.connect(self.handle_post_error)
        
        self.schedule_worker.schedule_update.connect(self.update_schedule_status)
        self.schedule_worker.trigger_post.connect(self.trigger_post)
        
        # Initialize UI
        self.init_ui()
        
        # Load saved data
        self.load_data()
        
        # Start schedule worker
        self.schedule_worker.start()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle("AI Influencer for Platform X")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_api_tab()
        self.create_content_tab()
        self.create_history_tab()
        self.create_settings_tab()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Add schedule status to status bar
        self.schedule_status = QLabel("Schedule: Not active")
        self.status_bar.addPermanentWidget(self.schedule_status)
    
    def create_dashboard_tab(self):
        """Create the dashboard tab."""
        dashboard_tab = QWidget()
        layout = QVBoxLayout(dashboard_tab)
        
        # Status section
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("System is ready")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_group)
        
        # Quick actions section
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.post_now_button = QPushButton("Post Now")
        self.post_now_button.clicked.connect(self.post_now)
        actions_layout.addWidget(self.post_now_button)
        
        self.test_api_button = QPushButton("Test API Connection")
        self.test_api_button.clicked.connect(self.test_api_connection)
        actions_layout.addWidget(self.test_api_button)
        
        self.view_last_post_button = QPushButton("View Last Post")
        self.view_last_post_button.clicked.connect(self.view_last_post)
        actions_layout.addWidget(self.view_last_post_button)
        
        layout.addWidget(actions_group)
        
        # Recent activity section
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_text = QTextEdit()
        self.activity_text.setReadOnly(True)
        activity_layout.addWidget(self.activity_text)
        
        layout.addWidget(activity_group)
        
        # Add tab
        self.tabs.addTab(dashboard_tab, "Dashboard")
    
    def create_api_tab(self):
        """Create the API credentials tab."""
        api_tab = QWidget()
        layout = QVBoxLayout(api_tab)
        
        # Twitter API credentials section
        twitter_group = QGroupBox("Twitter API Credentials")
        twitter_layout = QFormLayout(twitter_group)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        twitter_layout.addRow("API Key:", self.api_key_input)
        
        self.api_secret_input = QLineEdit()
        self.api_secret_input.setEchoMode(QLineEdit.Password)
        twitter_layout.addRow("API Secret:", self.api_secret_input)
        
        self.access_token_input = QLineEdit()
        self.access_token_input.setEchoMode(QLineEdit.Password)
        twitter_layout.addRow("Access Token:", self.access_token_input)
        
        self.access_token_secret_input = QLineEdit()
        self.access_token_secret_input.setEchoMode(QLineEdit.Password)
        twitter_layout.addRow("Access Token Secret:", self.access_token_secret_input)
        
        # Buttons for API credentials
        api_buttons_layout = QHBoxLayout()
        
        self.save_api_button = QPushButton("Save Credentials")
        self.save_api_button.clicked.connect(self.save_api_credentials)
        api_buttons_layout.addWidget(self.save_api_button)
        
        self.test_api_connection_button = QPushButton("Test Connection")
        self.test_api_connection_button.clicked.connect(self.test_api_connection)
        api_buttons_layout.addWidget(self.test_api_connection_button)
        
        twitter_layout.addRow("", api_buttons_layout)
        
        layout.addWidget(twitter_group)
        
        # OpenAI API credentials section
        openai_group = QGroupBox("OpenAI API Credentials (Optional)")
        openai_layout = QFormLayout(openai_group)
        
        self.openai_api_key_input = QLineEdit()
        self.openai_api_key_input.setEchoMode(QLineEdit.Password)
        openai_layout.addRow("API Key:", self.openai_api_key_input)
        
        # Button for OpenAI API
        openai_button_layout = QHBoxLayout()
        
        self.save_openai_button = QPushButton("Save OpenAI Key")
        self.save_openai_button.clicked.connect(self.save_openai_credentials)
        openai_button_layout.addWidget(self.save_openai_button)
        
        openai_layout.addRow("", openai_button_layout)
        
        layout.addWidget(openai_group)
        
        # Add spacer
        layout.addStretch()
        
        # Add tab
        self.tabs.addTab(api_tab, "API Credentials")
    
    def create_content_tab(self):
        """Create the content settings tab."""
        content_tab = QWidget()
        layout = QVBoxLayout(content_tab)
        
        # Topic preferences section
        topics_group = QGroupBox("Topic Preferences")
        topics_layout = QVBoxLayout(topics_group)
        
        # Create checkboxes for each category
        self.topic_checkboxes = {}
        for category in ["Bitcoin", "Lightning Network", "Nostr", "Privacy", "Node Setup"]:
            checkbox = QCheckBox(category)
            checkbox.setChecked(True)
            topics_layout.addWidget(checkbox)
            self.topic_checkboxes[category] = checkbox
        
        layout.addWidget(topics_group)
        
        # Posting schedule section
        schedule_group = QGroupBox("Posting Schedule")
        schedule_layout = QFormLayout(schedule_group)
        
        self.posting_interval = QSpinBox()
        self.posting_interval.setMinimum(1)
        self.posting_interval.setMaximum(168)  # 1 week in hours
        self.posting_interval.setValue(24)
        self.posting_interval.valueChanged.connect(self.update_posting_interval)
        schedule_layout.addRow("Hours between posts:", self.posting_interval)
        
        self.auto_posting = QCheckBox("Enable automatic posting")
        self.auto_posting.setChecked(True)
        self.auto_posting.stateChanged.connect(self.toggle_auto_posting)
        schedule_layout.addRow("", self.auto_posting)
        
        layout.addWidget(schedule_group)
        
        # Content preview section
        preview_group = QGroupBox("Content Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_button = QPushButton("Generate Preview")
        self.preview_button.clicked.connect(self.generate_preview)
        preview_layout.addWidget(self.preview_button)
        
        self.content_preview = QTextEdit()
        self.content_preview.setReadOnly(True)
        preview_layout.addWidget(self.content_preview)
        
        layout.addWidget(preview_group)
        
        # Add tab
        self.tabs.addTab(content_tab, "Content Settings")
    
    def create_history_tab(self):
        """Create the tweet history tab."""
        history_tab = QWidget()
        layout = QVBoxLayout(history_tab)
        
        # Create table for tweet history
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Date", "Category", "Topic", "Content", "Actions"])
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        
        layout.addWidget(self.history_table)
        
        # Add export button
        export_layout = QHBoxLayout()
        
        self.export_history_button = QPushButton("Export History")
        self.export_history_button.clicked.connect(self.export_history)
        export_layout.addWidget(self.export_history_button)
        
        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self.clear_history)
        export_layout.addWidget(self.clear_history_button)
        
        layout.addLayout(export_layout)
        
        # Add tab
        self.tabs.addTab(history_tab, "Tweet History")
    
    def create_settings_tab(self):
        """Create the settings tab."""
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        
        # General settings section
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout(general_group)
        
        self.data_dir_input = QLineEdit()
        self.data_dir_input.setText(os.path.join(os.path.dirname(__file__), 'data'))
        general_layout.addRow("Data Directory:", self.data_dir_input)
        
        self.browse_data_dir_button = QPushButton("Browse...")
        self.browse_data_dir_button.clicked.connect(self.browse_data_dir)
        general_layout.addRow("", self.browse_data_dir_button)
        
        layout.addWidget(general_group)
        
        # Image settings section
        image_group = QGroupBox("Image Settings")
        image_layout = QFormLayout(image_group)
        
        self.image_format_combo = QComboBox()
        self.image_format_combo.addItems(["Twitter (1200x675)", "Square (1080x1080)", "Portrait (1080x1350)"])
        image_layout.addRow("Image Format:", self.image_format_combo)
        
        layout.addWidget(image_group)
        
        # About section
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout(about_group)
        
        about_text = QLabel("AI Influencer for Platform X\nVersion 1.0.0\n\nA tool for automated content posting about Bitcoin, Lightning Network, Nostr, and related topics.")
        about_text.setAlignment(Qt.AlignCenter)
        about_layout.addWidget(about_text)
        
        layout.addWidget(about_group)
        
        # Add spacer
        layout.addStretch()
        
        # Add tab
        self.tabs.addTab(settings_tab, "Settings")
    
    def load_data(self):
        """Load saved data and settings."""
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Load API credentials
        credentials_file = os.path.join(data_dir, 'credentials.json')
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, 'r') as f:
                    credentials = json.load(f)
                
                # Set Twitter API credentials
                self.api_key_input.setText(credentials.get('twitter_api_key', ''))
                self.api_secret_input.setText(credentials.get('twitter_api_secret', ''))
                self.access_token_input.setText(credentials.get('twitter_access_token', ''))
                self.access_token_secret_input.setText(credentials.get('twitter_access_token_secret', ''))
                
                # Set OpenAI API key
                self.openai_api_key_input.setText(credentials.get('openai_api_key', ''))
                
                # Apply credentials to components
                self.apply_credentials()
                
                logger.info("Loaded credentials from file")
            except Exception as e:
                logger.error(f"Error loading credentials: {str(e)}")
        
        # Load settings
        settings_file = os.path.join(data_dir, 'settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Apply settings
                self.posting_interval.setValue(settings.get('posting_interval', 24))
                self.auto_posting.setChecked(settings.get('auto_posting', True))
                self.data_dir_input.setText(settings.get('data_dir', data_dir))
                
                # Apply topic preferences
                for category, checkbox in self.topic_checkboxes.items():
                    enabled = settings.get('topics', {}).get(category, True)
                    checkbox.setChecked(enabled)
                
                # Apply image format
                format_index = settings.get('image_format', 0)
                self.image_format_combo.setCurrentIndex(format_index)
                
                logger.info("Loaded settings from file")
            except Exception as e:
                logger.error(f"Error loading settings: {str(e)}")
        
        # Load tweet history
        history_file = os.path.join(data_dir, 'history.json')
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                # Populate history table
                self.update_history_table(history)
                
                # Add to activity log
                if history:
                    last_post = history[-1]
                    self.add_activity_log(f"Last post: {last_post.get('timestamp')} - {last_post.get('category')}: {last_post.get('topic')}")
                
                logger.info("Loaded tweet history from file")
            except Exception as e:
                logger.error(f"Error loading tweet history: {str(e)}")
    
    def save_data(self):
        """Save data and settings."""
        # Create data directory if it doesn't exist
        data_dir = self.data_dir_input.text()
        os.makedirs(data_dir, exist_ok=True)
        
        # Save API credentials
        credentials_file = os.path.join(data_dir, 'credentials.json')
        try:
            credentials = {
                'twitter_api_key': self.api_key_input.text(),
                'twitter_api_secret': self.api_secret_input.text(),
                'twitter_access_token': self.access_token_input.text(),
                'twitter_access_token_secret': self.access_token_secret_input.text(),
                'openai_api_key': self.openai_api_key_input.text()
            }
            
            with open(credentials_file, 'w') as f:
                json.dump(credentials, f, indent=2)
            
            logger.info("Saved credentials to file")
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
        
        # Save settings
        settings_file = os.path.join(data_dir, 'settings.json')
        try:
            # Get topic preferences
            topics = {}
            for category, checkbox in self.topic_checkboxes.items():
                topics[category] = checkbox.isChecked()
            
            settings = {
                'posting_interval': self.posting_interval.value(),
                'auto_posting': self.auto_posting.isChecked(),
                'data_dir': data_dir,
                'topics': topics,
                'image_format': self.image_format_combo.currentIndex()
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            logger.info("Saved settings to file")
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
    
    def apply_credentials(self):
        """Apply the entered credentials to the components."""
        # Set Twitter API credentials
        self.twitter_api.set_credentials(
            api_key=self.api_key_input.text(),
            api_secret=self.api_secret_input.text(),
            access_token=self.access_token_input.text(),
            access_token_secret=self.access_token_secret_input.text()
        )
        
        # Set OpenAI API key
        self.content_generator.set_api_key(self.openai_api_key_input.text())
    
    def save_api_credentials(self):
        """Save the API credentials."""
        self.apply_credentials()
        self.save_data()
        QMessageBox.information(self, "Success", "Twitter API credentials saved successfully.")
    
    def save_openai_credentials(self):
        """Save the OpenAI API credentials."""
        self.content_generator.set_api_key(self.openai_api_key_input.text())
        self.save_data()
        QMessageBox.information(self, "Success", "OpenAI API key saved successfully.")
    
    def test_api_connection(self):
        """Test the Twitter API connection."""
        self.update_status("Testing Twitter API connection...")
        
        # Apply current credentials
        self.apply_credentials()
        
        # Test authentication
        if self.twitter_api.authenticate():
            # Get user info
            user_info = self.twitter_api.get_user_info()
            if user_info:
                QMessageBox.information(
                    self, 
                    "Connection Successful", 
                    f"Successfully connected to Twitter API as @{user_info['screen_name']}."
                )
                self.update_status("Twitter API connection successful.")
                return
        
        # If we get here, there was an error
        QMessageBox.critical(
            self,
            "Connection Failed",
            "Failed to connect to Twitter API. Please check your credentials."
        )
        self.update_status("Twitter API connection failed.")
    
    def update_status(self, message: str):
        """
        Update the status display.
        
        Args:
            message: Status message
        """
        self.status_label.setText(message)
        self.status_bar.showMessage(message)
        self.add_activity_log(message)
        logger.info(message)
    
    def update_schedule_status(self, message: str):
        """
        Update the schedule status display.
        
        Args:
            message: Schedule status message
        """
        self.schedule_status.setText(message)
    
    def add_activity_log(self, message: str):
        """
        Add a message to the activity log.
        
        Args:
            message: Log message
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.activity_text.append(f"[{timestamp}] {message}")
    
    def post_now(self):
        """Manually trigger a post."""
        # Check if already posting
        if self.posting_worker.isRunning():
            QMessageBox.warning(self, "Posting in Progress", "A post is already being created. Please wait.")
            return
        
        # Apply current credentials
        self.apply_credentials()
        
        # Check if authenticated
        if not self.twitter_api.authenticate():
            QMessageBox.critical(self, "Authentication Failed", "Failed to authenticate with Twitter API. Please check your credentials.")
            return
        
        # Start posting worker
        self.update_status("Creating and posting content...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.posting_worker.start()
    
    def trigger_post(self):
        """Trigger a post from the scheduler."""
        # Only post if auto-posting is enabled
        if self.auto_posting.isChecked() and not self.posting_worker.isRunning():
            self.post_now()
    
    def handle_post_complete(self, result: Dict):
        """
        Handle completion of a post.
        
        Args:
            result: Post result data
        """
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Update status
        self.update_status(f"Post created successfully! Tweet ID: {result['tweet_id']}")
        
        # Save image to data directory
        data_dir = self.data_dir_input.text()
        images_dir = os.path.join(data_dir, 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"tweet_{timestamp}"
        
        saved_image = self.image_generator.save_image_to_file(
            result['image_path'],
            images_dir,
            image_filename
        )
        
        result['saved_image'] = saved_image
        
        # Add to history
        self.add_to_history(result)
        
        # Save data
        self.save_data()
    
    def handle_post_error(self, error_message: str):
        """
        Handle posting error.
        
        Args:
            error_message: Error message
        """
        # Hide progress bar
        self.progress_bar.setVisible(False)
        
        # Update status
        self.update_status(f"Error posting: {error_message}")
        
        # Show error message
        QMessageBox.critical(self, "Posting Error", f"An error occurred while posting: {error_message}")
    
    def add_to_history(self, post_data: Dict):
        """
        Add a post to the history.
        
        Args:
            post_data: Post data
        """
        # Load existing history
        data_dir = self.data_dir_input.text()
        history_file = os.path.join(data_dir, 'history.json')
        
        history = []
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
            except Exception as e:
                logger.error(f"Error loading history: {str(e)}")
        
        # Add new post
        history.append(post_data)
        
        # Save history
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.info("Saved post to history")
        except Exception as e:
            logger.error(f"Error saving history: {str(e)}")
        
        # Update history table
        self.update_history_table(history)
    
    def update_history_table(self, history: List[Dict]):
        """
        Update the history table with the provided history data.
        
        Args:
            history: List of post history items
        """
        # Clear table
        self.history_table.setRowCount(0)
        
        # Add rows
        for i, post in enumerate(reversed(history)):  # Show newest first
            self.history_table.insertRow(i)
            
            # Date
            timestamp = post.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            self.history_table.setItem(i, 0, QTableWidgetItem(timestamp))
            
            # Category
            self.history_table.setItem(i, 1, QTableWidgetItem(post.get('category', '')))
            
            # Topic
            self.history_table.setItem(i, 2, QTableWidgetItem(post.get('topic', '')))
            
            # Content
            self.history_table.setItem(i, 3, QTableWidgetItem(post.get('text', '')))
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_button = QPushButton("View")
            view_button.setProperty("post_index", i)
            view_button.clicked.connect(self.view_post)
            actions_layout.addWidget(view_button)
            
            self.history_table.setCellWidget(i, 4, actions_widget)
        
        # Resize columns
        self.history_table.resizeColumnsToContents()
    
    def view_post(self):
        """View details of a selected post."""
        # Get the post index from the sender button
        sender = self.sender()
        if not sender or not hasattr(sender, 'property'):
            return
        
        post_index = sender.property("post_index")
        if post_index is None:
            return
        
        # Load history
        data_dir = self.data_dir_input.text()
        history_file = os.path.join(data_dir, 'history.json')
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Get the post (accounting for reversed display)
            post = history[len(history) - 1 - post_index]
            
            # Create dialog to show post details
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Post Details")
            
            # Format post details
            details = f"Date: {post.get('timestamp', '')}\n"
            details += f"Category: {post.get('category', '')}\n"
            details += f"Topic: {post.get('topic', '')}\n\n"
            details += f"Content: {post.get('text', '')}\n\n"
            details += f"Hashtags: {' '.join(post.get('hashtags', []))}\n\n"
            details += f"Tweet ID: {post.get('tweet_id', '')}"
            
            dialog.setText(details)
            
            # Show image if available
            image_path = post.get('saved_image', '')
            if image_path and os.path.exists(image_path):
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Scale down if too large
                    if pixmap.width() > 400:
                        pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                    
                    dialog.setIconPixmap(pixmap)
            
            dialog.exec_()
            
        except Exception as e:
            logger.error(f"Error viewing post: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error viewing post: {str(e)}")
    
    def view_last_post(self):
        """View the most recent post."""
        # Load history
        data_dir = self.data_dir_input.text()
        history_file = os.path.join(data_dir, 'history.json')
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            if not history:
                QMessageBox.information(self, "No Posts", "No posts have been made yet.")
                return
            
            # Create a button with the index of the last post
            button = QPushButton()
            button.setProperty("post_index", 0)  # First row in the table (newest post)
            
            # Call view_post
            self.view_post.__get__(button, QPushButton)()
            
        except Exception as e:
            logger.error(f"Error viewing last post: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error viewing last post: {str(e)}")
    
    def export_history(self):
        """Export tweet history to a file."""
        # Load history
        data_dir = self.data_dir_input.text()
        history_file = os.path.join(data_dir, 'history.json')
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            if not history:
                QMessageBox.information(self, "No Data", "No posts to export.")
                return
            
            # Get export file path
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export History",
                os.path.join(os.path.expanduser("~"), "tweet_history.csv"),
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if not file_path:
                return
            
            # Export to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                f.write("Date,Category,Topic,Content,Hashtags,Tweet ID\n")
                
                for post in history:
                    date = post.get('timestamp', '')
                    category = post.get('category', '').replace('"', '""')
                    topic = post.get('topic', '').replace('"', '""')
                    content = post.get('text', '').replace('"', '""')
                    hashtags = ' '.join(post.get('hashtags', [])).replace('"', '""')
                    tweet_id = post.get('tweet_id', '')
                    
                    f.write(f'"{date}","{category}","{topic}","{content}","{hashtags}","{tweet_id}"\n')
            
            QMessageBox.information(self, "Export Successful", f"Tweet history exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting history: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error exporting history: {str(e)}")
    
    def clear_history(self):
        """Clear tweet history."""
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all tweet history? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Clear history file
        data_dir = self.data_dir_input.text()
        history_file = os.path.join(data_dir, 'history.json')
        
        try:
            with open(history_file, 'w') as f:
                json.dump([], f)
            
            # Clear table
            self.history_table.setRowCount(0)
            
            QMessageBox.information(self, "History Cleared", "Tweet history has been cleared.")
            
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error clearing history: {str(e)}")
    
    def generate_preview(self):
        """Generate a content preview."""
        # Apply current credentials
        self.apply_credentials()
        
        # Get enabled categories
        enabled_categories = []
        for category, checkbox in self.topic_checkboxes.items():
            if checkbox.isChecked():
                enabled_categories.append(category)
        
        if not enabled_categories:
            QMessageBox.warning(self, "No Categories", "Please enable at least one topic category.")
            return
        
        # Select a random category
        category = random.choice(enabled_categories)
        
        # Generate content
        try:
            self.update_status("Generating content preview...")
            
            if self.openai_api_key_input.text():
                content = self.content_generator.generate_content(category=category)
                if not content["success"]:
                    content = self.content_generator.generate_content_without_api(category=category)
            else:
                content = self.content_generator.generate_content_without_api(category=category)
            
            # Display preview
            preview_text = f"Category: {content['category']}\n"
            preview_text += f"Topic: {content['topic']}\n\n"
            preview_text += f"Text: {content['text']}\n\n"
            preview_text += f"Hashtags: {' '.join(content['hashtags'][:15])}\n\n"
            preview_text += f"Full post:\n{content['full_text_with_hashtags']}"
            
            self.content_preview.setText(preview_text)
            
            self.update_status("Content preview generated.")
            
        except Exception as e:
            logger.error(f"Error generating preview: {str(e)}")
            self.update_status(f"Error generating preview: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error generating preview: {str(e)}")
    
    def update_posting_interval(self, value: int):
        """
        Update the posting interval.
        
        Args:
            value: New interval in hours
        """
        self.schedule_worker.set_interval(value)
        self.save_data()
    
    def toggle_auto_posting(self, state: int):
        """
        Toggle automatic posting.
        
        Args:
            state: Checkbox state
        """
        if state == Qt.Checked:
            self.update_status("Automatic posting enabled")
        else:
            self.update_status("Automatic posting disabled")
        
        self.save_data()
    
    def browse_data_dir(self):
        """Browse for data directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Data Directory",
            self.data_dir_input.text()
        )
        
        if directory:
            self.data_dir_input.setText(directory)
            self.save_data()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save data
        self.save_data()
        
        # Stop workers
        self.posting_worker.stop()
        self.schedule_worker.stop()
        
        # Accept the event
        event.accept()


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    window = AIInfluencerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
