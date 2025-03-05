#!/bin/bash

# Set the current directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/update requirements
pip install --upgrade pip
pip install -r requirements.txt

# Special handling for PyAudio on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # Install portaudio with brew if not already installed
    if ! brew list portaudio &>/dev/null; then
        echo "Installing portaudio with Homebrew..."
        brew install portaudio
    fi
    
    # Set environment variables for PyAudio build
    export LDFLAGS="-L/usr/local/opt/portaudio/lib"
    export CPPFLAGS="-I/usr/local/opt/portaudio/include"
    
    # Try to install PyAudio
    pip install PyAudio
fi

# Run the application
python setup.py
