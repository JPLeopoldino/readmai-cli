import argparse
import os
import sys
import google.generativeai as genai

from .config.manager import ConfigManager
from .generator.readme import ReadmeGenerator

def main():
    parser = argparse.ArgumentParser(description="Generate a README.md for a project using Gemini AI.")
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="The path to the project directory (default: current directory).",
    )
    parser.add_argument(
        "--set-api-key",
        metavar="API_KEY",
        help="Set and save the Gemini API key to the configuration file.",
    )

    args = parser.parse_args()

    # Handle setting the API key
    if args.set_api_key:
        if ConfigManager.setup_config(args.set_api_key):
            sys.exit(0)
        else:
            sys.exit(1)

    # Resolve project path
    project_path = os.path.abspath(args.path if args.path is not None else ".")
    if not os.path.isdir(project_path):
        print(f"Error: Path '{project_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Configure API and generate README
    try:
        # Get and configure API key
        api_key = ConfigManager.resolve_api_key()
        genai.configure(api_key=api_key)
        
        # Generate README file
        generator = ReadmeGenerator()
        success = generator.generate(project_path)
        
        if not success:
            sys.exit(1)
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
