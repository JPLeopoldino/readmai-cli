import argparse
import os
import sys
import configparser
import google.generativeai as genai
from pathlib import Path
from halo import Halo

CONFIG_DIR = Path.home() / ".config" / "readmai"
CONFIG_FILE = CONFIG_DIR / "config.ini"

def setup_config(api_key=None):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    if api_key:
        config = configparser.ConfigParser()
        if CONFIG_FILE.exists():
            config.read(CONFIG_FILE)
        
        if "Credentials" not in config:
            config["Credentials"] = {}
        config["Credentials"]["api_key"] = api_key
        
        try:
            with open(CONFIG_FILE, "w") as configfile:
                config.write(configfile)
            os.chmod(CONFIG_FILE, 0o600)
            print(f"API key saved to {CONFIG_FILE}")
            return True
        except IOError as e:
            print(f"Error saving API key to {CONFIG_FILE}: {e}", file=sys.stderr)
            return False
    return True

def resolve_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        print("Using API key from GEMINI_API_KEY environment variable.")
        return api_key

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    
    if CONFIG_FILE.exists():
        try:
            if CONFIG_FILE.stat().st_mode & 0o077:
                print(f"Warning: Configuration file {CONFIG_FILE} has insecure permissions.", file=sys.stderr)
            config.read(CONFIG_FILE)
            api_key = config.get("Credentials", "api_key", fallback=None)
            if api_key:
                return api_key
        except Exception as e:
            print(f"Warning: Could not read configuration file: {e}", file=sys.stderr)

    api_key = input("Please enter your Gemini API key: ").strip()
    if not api_key:
        print("No API key provided. Exiting.", file=sys.stderr)
        sys.exit(1)

    setup_config(api_key)
    return api_key

def scan_project_structure(path):
    structure = []
    spinner = Halo(text='Scanning project structure...', spinner='dots')
    
    try:
        spinner.start()
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                       d not in ['node_modules', 'venv', '.venv', '__pycache__', 'build', 'dist', '.git']]
            files = [f for f in files if not f.startswith('.')]

            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * level
            structure.append(f'{indent}{os.path.basename(root)}/')
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                structure.append(f'{subindent}{f}')
        spinner.succeed('Scanning complete.')
    except Exception as e:
        spinner.fail(f'Scanning failed: {e}')
        raise
    finally:
        spinner.stop() if spinner else None
        
    return "\n".join(structure)

def clean_markdown(text):
    if text.startswith("```markdown\n"):
        text = text[len("```markdown\n"):]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("\n```"):
        text = text[:-len("\n```")]
    elif text.endswith("```"):
        text = text[:-3]
    return text

def generate_readme(project_path):
    spinner = None
    
    try:
        project_structure = scan_project_structure(project_path)
        if not project_structure:
            print("Could not find any relevant files in the project path.", file=sys.stderr)
            return

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
        spinner = Halo(text='Generating README with Gemini', spinner='dots')
        spinner.start()
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        spinner.succeed('README content generated.')

        if not response.parts:
            print("\nError: Gemini API returned an empty response.", file=sys.stderr)
            return

        readme_content = clean_markdown(response.text)
        readme_path = os.path.join(project_path, "README.md")
        
        print(f"Writing README.md to: {readme_path}")
        with open(readme_path, "w") as f:
            f.write(readme_content)
        print("README.md generated successfully.")

    except Exception as e:
        if spinner:
            spinner.fail(f'Generation failed: {e}')
        else:
            print(f"\nError generating README: {e}", file=sys.stderr)
    finally:
        if spinner:
            spinner.stop()

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

    if args.set_api_key:
        if setup_config(args.set_api_key):
            sys.exit(0)
        else:
            sys.exit(1)

    project_path = os.path.abspath(args.path if args.path is not None else ".")
    if not os.path.isdir(project_path):
        print(f"Error: Path '{project_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    try:
        genai.configure(api_key=resolve_api_key())
        generate_readme(project_path)
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error configuring Gemini API: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
