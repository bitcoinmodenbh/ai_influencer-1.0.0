#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User Guide for AI Influencer System

This document provides detailed instructions for using the AI Influencer system.
"""

# AI Influencer for Platform X - User Guide

## Introduction

Welcome to the AI Influencer system! This application automates content posting on your Platform X (Twitter) account, focusing on topics related to Bitcoin, Lightning Network, Nostr, online privacy, and related technologies.

This guide will walk you through all aspects of using the application, from initial setup to daily operation.

## Getting Started

### Installation

1. Ensure you have Python 3.8 or higher installed on your system
2. Install the application using one of these methods:
   - From source: `pip install .`
   - From the provided package: `pip install ai_influencer-1.0.0.tar.gz`

### First-Time Setup

When you first launch the application, you'll need to configure your API credentials:

1. Launch the application by running `python main.py` or `ai_influencer` if installed via pip
2. Navigate to the "API Credentials" tab
3. Enter your Twitter API credentials:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret
4. Click "Save Credentials"
5. Click "Test Connection" to verify your credentials work correctly

### Optional: OpenAI Integration

For enhanced content generation, you can add an OpenAI API key:

1. In the "API Credentials" tab, enter your OpenAI API key
2. Click "Save OpenAI Key"

If you don't provide an OpenAI API key, the system will use template-based content generation, which still produces good results.

## Using the Dashboard

The Dashboard is your main control center:

### System Status

- View the current status of the system
- See when the next scheduled post will occur
- Monitor any ongoing operations

### Quick Actions

- **Post Now**: Immediately create and post new content
- **Test API Connection**: Verify your Twitter API credentials
- **View Last Post**: See details of your most recent post

### Recent Activity

The activity log shows recent operations and their status, helping you track what the system has been doing.

## Managing Content Settings

The Content Settings tab allows you to customize what the system posts about:

### Topic Preferences

Enable or disable specific categories:
- Bitcoin
- Lightning Network
- Nostr
- Privacy
- Node Setup

The system will only post about enabled categories.

### Posting Schedule

- Set how frequently you want to post (in hours)
- Default is every 24 hours
- Enable or disable automatic posting

### Content Preview

Click "Generate Preview" to see an example of the content that will be posted, including:
- Selected category and topic
- Generated text
- Selected hashtags

This helps you verify the content meets your expectations before it's posted.

## Viewing Tweet History

The Tweet History tab maintains a record of all posts made by the system:

### History Table

- View all posts sorted by date (newest first)
- See the category, topic, and content of each post
- Click "View" to see full details including the image

### Export and Management

- **Export History**: Save your posting history as a CSV file
- **Clear History**: Remove all history records (use with caution)

## Configuring Settings

The Settings tab provides additional configuration options:

### General Settings

- **Data Directory**: Choose where the application stores data files
- This includes credentials, history, and generated images

### Image Settings

- **Image Format**: Choose the aspect ratio for generated images
  - Twitter (1200x675) - recommended for Twitter
  - Square (1080x1080)
  - Portrait (1080x1350)

## Automated Posting Process

When the system creates a post (either scheduled or manual), it follows this process:

1. Selects a topic from your enabled categories
2. Generates text content about that topic
3. Creates 15 relevant hashtags
4. Generates an image that complements the content
5. Posts the content and image to your Twitter account
6. Saves the post details to your history

## Troubleshooting

### Common Issues

#### Failed to Connect to Twitter API

- Verify your API credentials are correct
- Ensure your Twitter Developer account is active
- Check if you've reached API rate limits

#### Content Generation Issues

- If using OpenAI, verify your API key is valid
- The system will automatically fall back to template-based generation if needed

#### Image Generation Problems

- Ensure the application has write permissions to create temporary files
- Check if the data directory is accessible

### Getting Help

If you encounter issues not covered in this guide:

1. Check the application logs (ai_influencer.log)
2. Refer to the README.md file for additional information
3. Contact support with details about the issue

## Best Practices

### Optimal Usage

- **Posting Frequency**: Once per day is recommended for most accounts
- **Topic Variety**: Keep all topic categories enabled for diverse content
- **Regular Monitoring**: Check the application periodically to ensure it's running smoothly

### Account Management

- Regularly check your Twitter account to see engagement with posted content
- Respond to comments and interactions to boost engagement
- Use the insights from post performance to refine your topic preferences

## Conclusion

The AI Influencer system is designed to maintain a consistent presence for your personal account on Platform X with minimal effort. By automating the content creation and posting process, you can focus on engaging with your audience while ensuring regular, high-quality content about Bitcoin, Lightning Network, Nostr, and related topics.

Enjoy your automated social media presence!
