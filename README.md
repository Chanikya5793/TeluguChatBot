# Telugu Bus Information System

A voice-based bus information system that processes Telugu language queries.

## Quick Start

Run the launcher script:

```bash
python launcher.py
```

This script will:
1. Set the required API key
2. Check for dependencies
3. Run the appropriate interface

## Manual Installation

If you prefer to install dependencies yourself:

```bash
# Install required packages
pip install pygame SpeechRecognition PyAudio pymysql google-generativeai jinja2 gtts pydub pyttsx3 google-cloud-texttospeech pillow

# Set the API key
export GEMINI_API_KEY="AIzaSyAjwl7thjLDRZGKBazfq_b1BzWX-tN-0BU"

# Run the application
python cli.py
```

## File Structure

- **database.py**: Core backend with database queries and speech processing
- **cli.py**: Command-line interface with full audio support
- **simple_cli.py**: Minimal command-line interface
- **launcher.py**: Easy launcher script that handles the API key

The other files (setup.py, install.py, etc.) are support scripts but not needed for normal operation.

## Usage

After running the application:
1. Choose "Record Audio Query" from the menu
2. Speak your query in Telugu
3. The system will process your request and respond
