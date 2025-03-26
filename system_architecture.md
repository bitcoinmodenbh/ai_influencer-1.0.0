# AI Influencer System Architecture

## Overview

The AI Influencer system is designed to automatically manage a personal account on platform X (Twitter), publishing content on a 24-hour schedule about specific topics related to Bitcoin, Lightning Network, Nostr, and related technologies. The system consists of several interconnected modules that work together to generate and publish content, manage API connections, and provide a user interface for monitoring and configuration.

## System Components

### 1. Core Application

The core application serves as the central controller for the entire system, coordinating the activities of all other modules and maintaining the application state.

**Responsibilities:**
- Initialize and manage all system components
- Handle application configuration and settings
- Coordinate scheduled posting activities
- Manage error handling and logging
- Provide interfaces for user interaction

### 2. Twitter API Integration Module

This module handles all interactions with the Twitter API, including authentication, posting content, and retrieving account information.

**Responsibilities:**
- Securely store and manage API credentials
- Authenticate with the Twitter API
- Post text content to the platform
- Upload and attach images to posts
- Handle API rate limits and errors
- Retrieve account statistics and post history

### 3. Content Generation Module

The content generation module is responsible for creating engaging text content about the specified topics.

**Responsibilities:**
- Select topics based on configured preferences
- Generate informative and engaging text content
- Create relevant hashtags (15 per post)
- Ensure content meets platform requirements
- Maintain topic diversity over time

### 4. Image Generation Module

This module creates visually appealing images to accompany each post.

**Responsibilities:**
- Generate images related to the post content
- Ensure images meet platform size and format requirements
- Provide variety in image styles and themes
- Optimize images for engagement

### 5. Scheduler Module

The scheduler module manages the timing of posts according to the configured schedule.

**Responsibilities:**
- Maintain a 24-hour posting schedule
- Handle time zone considerations
- Provide flexibility for schedule adjustments
- Ensure reliable execution of scheduled tasks

### 6. Database Module

The database module handles persistent storage of application data.

**Responsibilities:**
- Store post history and content
- Maintain configuration settings
- Track posting statistics
- Provide data for the user interface

### 7. Graphical User Interface

The GUI provides a user-friendly interface for managing the application.

**Responsibilities:**
- Display system status and activity
- Provide API credential management
- Show post history and statistics
- Allow configuration of content preferences
- Enable schedule adjustments

## Data Flow

1. **Configuration Flow:**
   - User configures API credentials, content preferences, and schedule through the GUI
   - Configuration is stored in the database
   - Core application loads configuration and initializes modules

2. **Content Creation Flow:**
   - Scheduler triggers content creation at scheduled intervals
   - Content generation module creates text content and hashtags
   - Image generation module creates a related image
   - Combined content is prepared for posting

3. **Posting Flow:**
   - Twitter API module authenticates with the platform
   - Content and image are posted to the platform
   - Response from the API is processed
   - Post details are stored in the database
   - GUI is updated with the latest post information

4. **Monitoring Flow:**
   - GUI displays current system status
   - Post history and statistics are shown
   - Any errors or issues are logged and displayed

## Component Diagram

```
+-------------------+      +----------------------+
|                   |      |                      |
|  Graphical User   |<---->|  Core Application    |
|  Interface        |      |                      |
|                   |      +----------+-----------+
+-------------------+                 |
                                      |
                                      v
+-------------------+      +----------+-----------+      +-------------------+
|                   |      |                      |      |                   |
|  Database Module  |<---->|  Scheduler Module    |<---->|  Twitter API      |
|                   |      |                      |      |  Integration      |
+-------------------+      +----------+-----------+      +-------------------+
                                      |
                                      |
                    +-----------------+------------------+
                    |                                    |
                    v                                    v
        +----------------------+              +----------------------+
        |                      |              |                      |
        |  Content Generation  |              |  Image Generation    |
        |  Module              |              |  Module              |
        |                      |              |                      |
        +----------------------+              +----------------------+
```

## Database Schema

### Users Table
- user_id (primary key)
- username
- api_key (encrypted)
- api_secret (encrypted)
- access_token (encrypted)
- access_token_secret (encrypted)
- created_at
- updated_at

### Posts Table
- post_id (primary key)
- user_id (foreign key)
- content
- hashtags
- image_path
- platform_post_id
- posted_at
- status
- engagement_metrics

### Settings Table
- setting_id (primary key)
- user_id (foreign key)
- posting_frequency
- preferred_topics
- content_preferences
- created_at
- updated_at

### Topics Table
- topic_id (primary key)
- name
- category
- description
- priority

## Technology Stack

- **Programming Language:** Python 3.10+
- **GUI Framework:** PyQt5
- **API Integration:** Tweepy
- **Content Generation:** OpenAI API
- **Image Generation:** Pillow, Matplotlib
- **Database:** SQLite
- **Scheduling:** Schedule library
- **Configuration Management:** Python-dotenv

## Security Considerations

- API credentials are stored securely using encryption
- Authentication tokens are never exposed in logs or UI
- Regular validation of API connections
- Error handling to prevent unauthorized access
- Secure storage of generated content

## Scalability and Extensibility

The modular design allows for:
- Adding support for additional social media platforms
- Enhancing content generation capabilities
- Implementing more advanced image generation
- Adding analytics and reporting features
- Supporting multiple user accounts
