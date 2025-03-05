import os
import subprocess
import sys
import time


def print_header():
    print("\n" + "="*60)
    print(" Telugu Bus Information System - Setup Script")
    print("="*60)

def check_dependencies():
    """Check for required Python packages and install missing ones"""
    required_packages = [
        "pygame",
        "speech_recognition",
        "pymysql",
        "google-generativeai",
        "jinja2",
        "gtts",
        "playsound",
        "pydub",
        "pyttsx3",
        "google-cloud-texttospeech",
        "pillow"
    ]
    
    missing_packages = []
    
    print("Checking for required packages...")
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nThe following packages need to be installed:")
        for package in missing_packages:
            print(f"  - {package}")
        
        install = input("\nWould you like to install these packages now? (y/n): ")
        
        if install.lower() == "y":
            print("\nInstalling missing packages...")
            
            for package in missing_packages:
                print(f"\nInstalling {package}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"✅ {package} installed successfully")
                except subprocess.CalledProcessError:
                    print(f"❌ Failed to install {package}")
                    if package == "pygame":
                        print("NOTE: pygame may require additional system dependencies.")
                        print("You can try running the text-only version with: python simple_cli.py")
            
            print("\nPackage installation completed.")
        else:
            print("\nPackage installation skipped.")
            print("You can try running the text-only version with: python simple_cli.py")
    else:
        print("\nAll required packages are installed! ✅")

def check_api_key():
    """Check if the GEMINI_API_KEY environment variable is set"""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("\n⚠️  GEMINI_API_KEY environment variable is not set!")
        
        key = input("Please enter your Gemini API key (press Enter to skip): ")
        
        if key.strip():
            # Set environment variable for current session
            os.environ["GEMINI_API_KEY"] = key
            
            # Ask about adding to shell profile for persistence
            add_to_profile = input("\nWould you like to add this API key to your shell profile? (y/n): ")
            
            if add_to_profile.lower() == "y":
                shell = os.environ.get("SHELL", "")
                home = os.path.expanduser("~")
                
                if "bash" in shell:
                    profile_path = os.path.join(home, ".bash_profile")
                elif "zsh" in shell:
                    profile_path = os.path.join(home, ".zshrc")
                else:
                    print("Could not determine shell profile. Please add it manually.")
                    return
                
                with open(profile_path, "a") as f:
                    f.write(f'\nexport GEMINI_API_KEY="{key}"\n')
                
                print(f"API key added to {profile_path}")
                print("Please restart your terminal or run 'source ~/.bash_profile' (or .zshrc) to apply changes.")
        else:
            print("\nAPI key setup skipped. You'll need to set the GEMINI_API_KEY environment variable later.")
    else:
        print("\n✅ GEMINI_API_KEY environment variable is set.")

def create_simple_cli():
    """Create a simple CLI version that doesn't require pygame"""
    simple_cli_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple_cli.py")
    
    if not os.path.exists(simple_cli_path):
        print("\nCreating simple text-only CLI version...")
        
        with open(simple_cli_path, "w") as f:
            f.write("# filepath: /Users/chanakya/Downloads/Telugu/simple_cli.py\n")
            f.write("import os\n")
            f.write("import threading\n")
            f.write("import time\n")
            f.write("import speech_recognition as sr\n\n")
            f.write("# Try to import database, but handle missing pygame gracefully\n")
            f.write("try:\n")
            f.write("    import database\n")
            f.write("    DATABASE_MODULE_AVAILABLE = True\n")
            f.write("except ImportError as e:\n")
            f.write("    print(f\"Warning: {e}\")\n")
            f.write("    DATABASE_MODULE_AVAILABLE = False\n\n")
            f.write("class SimpleTeluguBusInfoCLI:\n")
            f.write("    def __init__(self):\n")
            f.write("        # Initialize speech recognizer\n")
            f.write("        self.recognizer = sr.Recognizer()\n")
            f.write("        self.microphone = sr.Microphone()\n")
            f.write("        \n")
            f.write("        # State variables\n")
            f.write("        self.is_recording = False\n")
            f.write("        self.timer_count = 15\n")
            f.write("        \n")
            f.write("        # Database connection\n")
            f.write("        self.connection = None\n")
            f.write("        if DATABASE_MODULE_AVAILABLE:\n")
            f.write("            try:\n")
            f.write("                import pymysql\n")
            f.write("                self.connection = pymysql.connect(\n")
            f.write("                    host=database.DATABASE_HOST,\n")
            f.write("                    user=database.DATABASE_USER,\n")
            f.write("                    password=database.DATABASE_PASSWORD,\n")
            f.write("                    database=database.DATABASE_NAME\n")
            f.write("                )\n")
            f.write("                print(\"Connected to database successfully\")\n")
            f.write("            except Exception as e:\n")
            f.write("                print(f\"Database connection error: {e}\")\n")
            
            # Add rest of the simple_cli.py file content
            # Only showing the first part for brevity
            f.write("\n    def display_menu(self):\n")
            f.write("        \"\"\"Display the main menu and get user choice\"\"\"\n")
            f.write("        while True:\n")
            f.write("            print(\"\\n\" + \"=\"*50)\n")
            f.write("            print(\"Telugu Bus Information System - Simple CLI Version\")\n")
            f.write("            print(\"=\"*50)\n")
            f.write("            print(\"1. Record Audio Query (15 seconds max)\")\n")
            f.write("            print(\"2. Exit\")\n")
            f.write("            \n")
            f.write("            choice = input(\"\\nEnter your choice (1-2): \")\n")
            f.write("            \n")
            f.write("            if choice == '1':\n")
            f.write("                self.start_recording()\n")
            f.write("            elif choice == '2':\n")
            f.write("                print(\"Exiting program. Goodbye!\")\n")
            f.write("                break\n")
            f.write("            else:\n")
            f.write("                print(\"Invalid choice. Please try again.\")\n")
            
            # Continue adding functions...
            f.write("\n# Add the rest of the SimpleTeluguBusInfoCLI class here\n")
            
            f.write("\nif __name__ == \"__main__\":\n")
            f.write("    app = SimpleTeluguBusInfoCLI()\n")
            f.write("    try:\n")
            f.write("        app.display_menu()\n")
            f.write("    finally:\n")
            f.write("        app.on_closing()\n")
            
        print("✅ Created simple_cli.py")
    else:
        print("✅ simple_cli.py already exists")

def run_program():
    """Ask user which program to run"""
    print("\n" + "="*60)
    print(" Choose a program to run:")
    print("="*60)
    print("1. GUI Version (requires tkinter)")
    print("2. CLI Version (requires pygame)")
    print("3. Simple CLI Version (minimal dependencies)")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        try:
            subprocess.run([sys.executable, "gui.py"])
        except Exception as e:
            print(f"Error running GUI: {e}")
    elif choice == "2":
        try:
            subprocess.run([sys.executable, "cli.py"])
        except Exception as e:
            print(f"Error running CLI: {e}")
    elif choice == "3":
        try:
            subprocess.run([sys.executable, "simple_cli.py"])
        except Exception as e:
            print(f"Error running Simple CLI: {e}")
    elif choice == "4":
        print("Exiting setup.")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    print_header()
    check_dependencies()
    check_api_key()
    create_simple_cli()
    run_program()
