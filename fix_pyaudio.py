#!/usr/bin/env python3
import os
import subprocess
import sys
import platform

def print_header():
    print("\n" + "="*60)
    print(" PyAudio Installation Fix for macOS ".center(60))
    print("="*60)

def run_command(command):
    """Run a shell command and return its output"""
    try:
        print(f"Running: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
            if result.stderr:
                print(f"Error output: {result.stderr}")
        return result.stdout
    except Exception as e:
        print(f"Error executing command: {e}")
        return None

def uninstall_pyaudio():
    print("\nUninstalling existing PyAudio installation...")
    run_command([sys.executable, "-m", "pip", "uninstall", "-y", "pyaudio"])

def install_portaudio():
    print("\nInstalling PortAudio with Homebrew...")
    if platform.system() != "Darwin":
        print("This script is designed for macOS only.")
        return False
    
    # Check if Homebrew is installed
    brew_path = run_command(["which", "brew"]).strip()
    if not brew_path:
        print("Homebrew is not installed. Please install Homebrew first:")
        print("    /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    
    # Install or reinstall portaudio
    print("Installing/reinstalling portaudio...")
    run_command(["brew", "uninstall", "--ignore-dependencies", "portaudio"])
    run_command(["brew", "install", "portaudio"])
    
    return True

def install_pyaudio():
    print("\nInstalling PyAudio with proper environment variables...")
    # Set environment variables for building PyAudio
    os.environ["LDFLAGS"] = "-L/usr/local/lib"
    os.environ["CPPFLAGS"] = "-I/usr/local/include"
    
    # Install PyAudio
    run_command([sys.executable, "-m", "pip", "install", "--force-reinstall", "pyaudio"])

def test_pyaudio():
    print("\nTesting PyAudio installation...")
    try:
        import pyaudio
        print("PyAudio version:", pyaudio.get_portaudio_version_text())
        print("✅ PyAudio is working correctly!")
        return True
    except ImportError as e:
        print(f"❌ PyAudio import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ PyAudio test failed: {e}")
        return False

def main():
    print_header()
    
    if platform.system() != "Darwin":
        print("This script is designed for macOS only.")
        return
    
    print("This script will fix PyAudio installation by:")
    print("1. Uninstalling any existing PyAudio")
    print("2. Installing/reinstalling PortAudio with Homebrew")
    print("3. Installing PyAudio with the correct environment variables")
    
    proceed = input("\nProceed? (y/n): ")
    if proceed.lower() != 'y':
        print("Operation cancelled.")
        return
    
    uninstall_pyaudio()
    if install_portaudio():
        install_pyaudio()
        if test_pyaudio():
            print("\n" + "="*60)
            print(" PyAudio successfully installed! ".center(60))
            print("="*60)
            print("\nYou can now run the Telugu Bus Information System:")
            print("python launcher.py")
        else:
            print("\n⚠️ PyAudio installation still has issues.")
            print("You might need to try an alternative approach:")
            print("1. Install Python 3.9 or 3.10 (older versions tend to have fewer issues)")
            print("2. Use 'pip3.9 install pyaudio' with that version")
            print("Or consider using the text-only version that doesn't require audio recording:")
            print("python text_mode.py")
    else:
        print("\nFailed to install PortAudio. Please install it manually.")

if __name__ == "__main__":
    main()
