#!/usr/bin/env python3
import os
import platform
import subprocess
import sys


def print_header():
    print("\n" + "="*70)
    print(" Telugu Bus Information System - Simple Install Script")
    print("="*70)

def install_packages():
    print("\nInstalling required packages...")
    
    # List of packages to install
    packages = [
        "pygame",
        "SpeechRecognition",
        "PyAudio",
        "pymysql",
        "google-generativeai",
        "jinja2",
        "gtts",
        "pydub",
        "pyttsx3",
        "google-cloud-texttospeech",
        "pillow"
    ]
    
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def check_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("\n⚠️  GEMINI_API_KEY environment variable is not set!")
        key = input("Please enter your Gemini API key (press Enter to skip): ")
        
        if key.strip():
            os.environ["GEMINI_API_KEY"] = key
            print("\nAPI key set for current session")
        else:
            print("\nAPI key setup skipped.")

def run_cli():
    print("\nRunning simple CLI version...")
    try:
        subprocess.run([sys.executable, "simple_cli.py"])
    except Exception as e:
        print(f"Error running CLI: {e}")

if __name__ == "__main__":
    print_header()
    install_packages()
    check_api_key()
    
    print("\nSetup complete! You can now run:")
    print("python simple_cli.py")
    
    run_now = input("\nWould you like to run the application now? (y/n): ")
    if run_now.lower() == 'y':
        run_cli()
