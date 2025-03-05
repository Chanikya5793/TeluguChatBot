#!/usr/bin/env python3
import os
import platform
import subprocess
import sys


def print_header():
    print("\n" + "="*70)
    print(" Telugu Bus Information System - Installation Helper".center(70))
    print("="*70)

def run_command(command):
    """Run a shell command and return its success status"""
    try:
        print(f"Running: {' '.join(command)}")
        subprocess.check_call(command)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        return False

def check_virtual_env():
    """Check if running inside a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def create_and_activate_venv():
    """Create a virtual environment if one doesn't exist"""
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.venv')
    
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment at {venv_path}...")
        run_command([sys.executable, '-m', 'venv', venv_path])
    
    # Return the path to the Python executable in the venv
    if platform.system() == 'Windows':
        return os.path.join(venv_path, 'Scripts', 'python')
    else:
        return os.path.join(venv_path, 'bin', 'python')

def fix_requirements_file():
    """Fix the requirements file with correct package names"""
    req_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
    correct_requirements = """pygame
SpeechRecognition
PyAudio
pymysql
google-generativeai
jinja2
gtts
playsound
pydub
pyttsx3
google-cloud-texttospeech
pillow
"""
    
    with open(req_path, 'w') as f:
        f.write(correct_requirements)
    
    print(f"Updated requirements file at {req_path}")

def install_system_dependencies():
    """Install system dependencies based on the OS"""
    system = platform.system()
    
    if system == 'Darwin':  # macOS
        print("\nChecking macOS dependencies...")
        
        # Check if Homebrew is installed
        if not run_command(['which', 'brew']):
            print("Homebrew is not installed. Please install Homebrew first:")
            print("    /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return False
        
        # Check for portaudio (needed for PyAudio)
        print("\nInstalling system dependencies with Homebrew...")
        run_command(['brew', 'install', 'portaudio', 'sdl2', 'sdl2_mixer', 'sdl2_image', 'sdl2_ttf'])
        
        # Set up environment variables for building packages
        os.environ['LDFLAGS'] = "-L/usr/local/opt/portaudio/lib"
        os.environ['CPPFLAGS'] = "-I/usr/local/opt/portaudio/include"
        
    elif system == 'Linux':
        # For Debian/Ubuntu-based systems
        print("\nChecking Linux dependencies (assuming Debian/Ubuntu)...")
        run_command(['sudo', 'apt-get', 'update'])
        run_command(['sudo', 'apt-get', 'install', '-y', 'python3-dev', 'portaudio19-dev', 'python3-pyaudio', 'libsdl2-dev', 'libsdl2-mixer-dev', 'libsdl2-image-dev', 'libsdl2-ttf-dev'])
    
    elif system == 'Windows':
        print("\nOn Windows, you may need to install PyAudio and pygame separately.")
        print("If you encounter issues, try downloading PyAudio wheel from:")
        print("https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
    
    return True

def install_python_dependencies(python_executable):
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    
    # Update pip first
    run_command([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    
    # Install requirements
    success = run_command([python_executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    
    # If standard installation fails, try installing packages one by one
    if not success:
        print("\nFull installation failed. Trying to install packages individually...")
        with open('requirements.txt', 'r') as f:
            packages = [line.strip() for line in f.readlines() if line.strip()]
        
        for package in packages:
            print(f"\nAttempting to install {package}...")
            run_command([python_executable, '-m', 'pip', 'install', package])

def create_activation_script():
    """Create a script to run the application with the correct environment"""
    system = platform.system()
    
    if system == 'Windows':
        with open('run.bat', 'w') as f:
            f.write('@echo off\n')
            f.write(r'.venv\Scripts\python setup.py' + '\n')
        print("\nCreated run.bat file. Run the application with: run.bat")
    else:
        with open('run.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('source .venv/bin/activate\n')
            f.write('python setup.py\n')
        
        # Make the script executable
        os.chmod('run.sh', 0o755)
        print("\nCreated run.sh file. Run the application with: ./run.sh")

def main():
    print_header()
    
    # Check if we're in a virtual environment
    if not check_virtual_env():
        print("Not running in a virtual environment. Creating one...")
        venv_python = create_and_activate_venv()
        
        print("\nVirtual environment created, but we need to rerun this script inside it.")
        print("Please run the following commands:")
        
        if platform.system() == 'Windows':
            print(f"\n    .venv\\Scripts\\pip install -e .")
            print(f"    .venv\\Scripts\\python {os.path.basename(__file__)}")
        else:
            print(f"\n    source .venv/bin/activate")
            print(f"    python {os.path.basename(__file__)}")
        
        return
    
    print("Running in virtual environment ✓")
    
    # Fix requirements file
    fix_requirements_file()
    
    # Install system dependencies
    install_system_dependencies()
    
    # Install Python dependencies
    install_python_dependencies(sys.executable)
    
    # Create activation script
    create_activation_script()
    
    print("\n" + "="*70)
    print(" Installation Complete ".center(70))
    print("="*70)
    print("\nTo run the Telugu Bus Information System:")
    
    if platform.system() == 'Windows':
        print("    run.bat")
    else:
        print("    ./run.sh")

if __name__ == "__main__":
    main()
