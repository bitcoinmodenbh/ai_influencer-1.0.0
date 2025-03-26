#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Application for AI Influencer System

This module serves as the entry point for the AI Influencer application.
"""

import os
import sys
import logging
from PyQt5.QtWidgets import QApplication
from gui import AIInfluencerGUI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ai_influencer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Main")

def main():
    """Main function to run the application."""
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
        
        # Create assets directories if they don't exist
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        os.makedirs(os.path.join(assets_dir, 'backgrounds'), exist_ok=True)
        os.makedirs(os.path.join(assets_dir, 'icons'), exist_ok=True)
        os.makedirs(os.path.join(assets_dir, 'fonts'), exist_ok=True)
        
        # Start the application
        app = QApplication(sys.argv)
        window = AIInfluencerGUI()
        window.show()
        
        logger.info("Application started successfully")
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        print(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
