#!/usr/bin/env python3
import os
import sys
import subprocess

# Set the Gemini API key directly in the script
os.environ["GEMINI_API_KEY"] = "AIzaSyAjwl7thjLDRZGKBazfq_b1BzWX-tN-0BU"

print("Telugu Bus Information System Launcher")
print("======================================")
print("\nGEMINI_API_KEY has been set for this session.")

# Check if pygame is installed
try:
    import pygame
    print("✅ pygame is installed")
    has_pygame = True
except ImportError:
    print("❌ pygame is not installed")
    has_pygame = False

# Check if other dependencies are installed
try:
    import speech_recognition
    print("✅ SpeechRecognition is installed")
    has_sr = True
except ImportError:
    print("❌ SpeechRecognition is not installed")
    has_sr = False

# Determine which file to run
if has_pygame and has_sr:
    print("\nRunning command-line interface with audio playback...")
    subprocess.run([sys.executable, "cli.py"])
elif has_sr:
    print("\nRunning simple command-line interface...")
    subprocess.run([sys.executable, "simple_cli.py"])
else:
    print("\nError: SpeechRecognition is required to run this application.")
    print("Please install it using: pip install SpeechRecognition")
