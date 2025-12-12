"""
ResumeMatchAI - ATS Resume Scanner
Main entry point for the application.
"""

import subprocess
import sys
import os

def main():
    """Main entry point for ResumeMatchAI."""
    print("🚀 ResumeMatchAI - ATS Resume Scanner")
    print("=" * 50)
    print("Advanced ATS scoring for job seekers and recruiters")
    print()

    # Check if running as main script
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "--version":
            print("ResumeMatchAI v1.0.0")
            return
        elif command == "--help":
            print_usage()
            return

    # Default behavior: start Streamlit app
    print("Starting Streamlit application...")
    print("Open your browser to http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print()

    try:
        # Run streamlit app
        app_path = os.path.join(os.path.dirname(__file__), "app.py")
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path],
                      check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting application: {e}")
        print("Make sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        sys.exit(0)

def print_usage():
    """Print usage information."""
    print("Usage: python main.py [command]")
    print()
    print("Commands:")
    print("  (no command)    Start the Streamlit web application")
    print("  --version        Show version information")
    print("  --help          Show this help message")
    print()
    print("Examples:")
    print("  python main.py              # Start web app")
    print("  streamlit run app.py       # Alternative way to start")
    print()
    print("For more information, visit: https://github.com/yourusername/ResumeMatchAI")

if __name__ == "__main__":
    main()
