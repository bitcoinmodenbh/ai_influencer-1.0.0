# AI Influencer for Platform X

A Python application that automatically manages a personal account on platform X (Twitter), publishing content on a 24-hour schedule about Bitcoin, Lightning Network, Nostr, online privacy, and related topics.

## Features

- **Automated Content Generation**: Creates engaging posts about Bitcoin, Lightning Network, Nostr, online privacy, and node setup topics
- **Image Generation**: Automatically generates relevant images to accompany each post
- **Hashtag Generation**: Includes 15 relevant hashtags with each post for maximum visibility
- **Scheduled Posting**: Posts content on a configurable schedule (default: every 24 hours)
- **Twitter API Integration**: Securely connects to your Twitter account
- **Graphical User Interface**: Easy-to-use interface for managing all aspects of the system
- **Post History**: Keeps track of all published posts with export capabilities

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. Clone the repository or download the source code:
   ```
   git clone https://github.com/yourusername/ai_influencer.git
   cd ai_influencer
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

   Or install using setup.py:
   ```
   pip install .
   ```

## Configuration

Before using the application, you need to set up your API credentials:

### Twitter API Credentials

1. Create a Twitter Developer account at [developer.twitter.com](https://developer.twitter.com/)
2. Create a new project and app
3. Generate API keys and access tokens
4. Add these credentials to the application through the GUI or by creating a `.env` file based on the `.env.template`

### OpenAI API (Optional)

For enhanced content generation:

1. Create an account at [openai.com](https://openai.com/)
2. Generate an API key
3. Add the API key to the application through the GUI or in the `.env` file

## Usage

### Starting the Application

Run the application using:

```
python main.py
```

Or if installed via pip:

```
ai_influencer
```

### Using the GUI

The application has a tabbed interface with the following sections:

#### Dashboard

- View system status
- Trigger manual posts
- Test API connections
- View recent activity

#### API Credentials

- Enter and save Twitter API credentials
- Enter and save OpenAI API credentials (optional)
- Test API connections

#### Content Settings

- Select topic preferences
- Configure posting schedule
- Generate content previews

#### Tweet History

- View all published posts
- Export history to CSV
- Clear history

#### Settings

- Configure data directory
- Set image format preferences

## Automated Posting

The application will automatically post content based on your configured schedule (default: every 24 hours). You can:

- Enable/disable automatic posting
- Change the posting frequency
- Manually trigger posts at any time

## Customization

### Topic Preferences

You can customize which topics the system posts about by enabling/disabling categories in the Content Settings tab:

- Bitcoin
- Lightning Network
- Nostr
- Online Privacy
- Node Setup

### Image Customization

The system generates images based on the post content and category. You can select from different image formats in the Settings tab.

## Troubleshooting

### API Connection Issues

If you experience issues connecting to the Twitter API:

1. Verify your API credentials are correct
2. Ensure your Twitter Developer account is in good standing
3. Check if you've exceeded API rate limits

### Content Generation Issues

If content generation fails:

1. Check if your OpenAI API key is valid (if using OpenAI)
2. The system will automatically fall back to template-based generation if API generation fails

## Development

### Project Structure

- `twitter_api.py`: Twitter API integration module
- `content_generator.py`: Content generation module
- `image_generator.py`: Image generation module
- `gui.py`: Graphical user interface module
- `main.py`: Main application entry point
- `tests/`: Test modules

### Running Tests

Run the unit tests:

```
python -m unittest discover
```

Run integration tests:

```
python -m unittest tests/test_integration.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and PyQt5
- Uses the Tweepy library for Twitter API integration
- Uses Pillow and Matplotlib for image generation
