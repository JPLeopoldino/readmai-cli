import argparse
import os
import google.generativeai as genai
import sys
import configparser
from pathlib import Path
from halo import Halo  # Import halo
import time

CONFIG_DIR = Path.home() / ".config" / "readmai"
CONFIG_FILE = CONFIG_DIR / "config.ini"

def ensure_config_dir_exists():
    """Ensures the configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def save_api_key_to_config(api_key):
    """Saves the API key to the configuration file."""
    ensure_config_dir_exists()
    config = configparser.ConfigParser()
    # Read existing config to avoid overwriting other potential settings
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    if "Credentials" not in config:
        config["Credentials"] = {}
    config["Credentials"]["api_key"] = api_key
    try:
        with open(CONFIG_FILE, "w") as configfile:
            config.write(configfile)
        # Ensure the file has restricted permissions
        os.chmod(CONFIG_FILE, 0o600)  # Read/write for owner only
        print(f"API key saved to {CONFIG_FILE}")
        return True
    except IOError as e:
        print(f"Error saving API key to {CONFIG_FILE}: {e}", file=sys.stderr)
        return False

def get_api_key():
    """Gets the API key from env var, config file, or prompts the user."""
    # 1. Check environment variable first
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print("Using API key from GEMINI_API_KEY environment variable.")
        return api_key

    # 2. Check configuration file
    ensure_config_dir_exists()  # Ensure dir exists before reading
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        try:
            # Check permissions before reading
            if CONFIG_FILE.stat().st_mode & 0o077:
                print(f"Warning: Configuration file {CONFIG_FILE} has insecure permissions. Consider running `chmod 600 {CONFIG_FILE}`.", file=sys.stderr)
            config.read(CONFIG_FILE)
            api_key = config.get("Credentials", "api_key", fallback=None)
            if api_key:
                return api_key
        except (configparser.Error, OSError) as e:
            print(f"Warning: Could not read configuration file {CONFIG_FILE}: {e}", file=sys.stderr)

    # 3. Prompt user if not found
    print("Gemini API key not found in environment variables or configuration file.")
    api_key = input("Please enter your Gemini API key: ").strip()

    if not api_key:
        print("No API key provided. Exiting.", file=sys.stderr)
        sys.exit(1)

    # 4. Save the key to the configuration file
    save_api_key_to_config(api_key)

    return api_key

def get_project_structure(path):
    """Gets a string representation of the project directory structure."""
    structure = []
    spinner = Halo(text='Scanning project structure...', spinner='dots')
    try:
        spinner.start()
        for root, dirs, files in os.walk(path):
            # Ignore hidden files/dirs and common virtual environments/build artifacts
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '.venv', '__pycache__', 'build', 'dist', '.git']]
            files = [f for f in files if not f.startswith('.')]

            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * (level)
            structure.append(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                structure.append(f'{subindent}{f}')
        spinner.succeed('Scanning complete.')
    except Exception as e:
        spinner.fail(f'Scanning failed: {e}')
        raise  # Re-raise the exception after stopping the spinner
    finally:
        if spinner:  # Check if spinner object exists
            spinner.stop()
    return "\n".join(structure)

def generate_readme(project_path):
    """Generates a README.md file for the given project path using Gemini AI."""
    spinner = None  # Initialize spinner variable
    try:
        project_structure = get_project_structure(project_path)
        if not project_structure:
            print("Could not find any relevant files in the project path.", file=sys.stderr)
            return

        # TODO: Refine this prompt for better results
        prompt = f"""
Generate a README.md file for a project with the following structure:

{project_structure}

Describe the project confidently and factually based *only* on the provided file structure. Avoid speculative language like 'appears to be', 'likely', 'might be', or 'seems to'. State what the project *is* based on the structure.

The README must include:
- A definitive description of the project based on its structure.
- Instructions on how to install or set up the project (provide clear steps or placeholders if details cannot be inferred).
- Instructions on how to use the project (provide clear steps or placeholders if details cannot be inferred).
- Any other relevant sections clearly indicated by the file structure (e.g., tests, examples).

Format the output as Markdown.
"""

        model = genai.GenerativeModel('gemini-2.0-flash')

        # Use Halo spinner for the API call
        spinner = Halo(text='Generating README with Gemini', spinner='dots')
        spinner.start()

        response = model.generate_content(prompt)
        spinner.succeed('README content generated.')  # Change text on success

        if not response.parts:
            spinner.stop()  # Or spinner.fail()
            print("\nError: Gemini API returned an empty response. This might be due to safety settings or prompt issues.", file=sys.stderr)
            return

        readme_content = response.text

        if readme_content.startswith("```markdown\n"):
            readme_content = readme_content[len("```markdown\n"):]
        if readme_content.startswith("```"):
            readme_content = readme_content[3:]
        if readme_content.endswith("\n```"):
            readme_content = readme_content[:-len("\n```")]
        elif readme_content.endswith("```"):
            readme_content = readme_content[:-3]

        readme_path = os.path.join(project_path, "README.md")

        print(f"Writing README.md to: {readme_path}")
        with open(readme_path, "w") as f:
            f.write(readme_content)
        print("README.md generated successfully.")

    except Exception as e:
        if spinner:  # Check if spinner object exists before trying to fail it
            spinner.fail(f'Generation failed: {e}')
        else:
            print(f"\nError generating README: {e}", file=sys.stderr)
    finally:
        if spinner:  # Check if spinner object exists
            spinner.stop()

def main():
    parser = argparse.ArgumentParser(description="Generate a README.md for a project using Gemini AI.")
    parser.add_argument(
        "path",
        nargs="?",
        default=None,  # Default to None to distinguish between no path and '.'
        help="The path to the project directory (default: current directory if no other action is taken).",
    )
    parser.add_argument(
        "--set-api-key",
        metavar="API_KEY",
        help="Set and save the Gemini API key to the configuration file.",
    )

    args = parser.parse_args()

    # Handle setting the API key
    if args.set_api_key:
        if save_api_key_to_config(args.set_api_key):
            sys.exit(0)  # Exit successfully after saving
        else:
            sys.exit(1)  # Exit with error if saving failed

    # If --set-api-key was not used, proceed with README generation
    project_path_arg = args.path if args.path is not None else "."
    project_path = os.path.abspath(project_path_arg)

    if not os.path.isdir(project_path):
        print(f"Error: Path '{project_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Configure the API key (only if not setting the key)
    try:
        active_api_key = get_api_key()  # This will prompt if needed
        genai.configure(api_key=active_api_key)
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        print("Please set the GEMINI_API_KEY environment variable or provide the key when prompted.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error configuring Gemini API: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate the README
    generate_readme(project_path)

if __name__ == "__main__":
    main()
