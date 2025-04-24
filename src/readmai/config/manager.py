import os
import sys
import configparser
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "readmai"
CONFIG_FILE = CONFIG_DIR / "config.ini"

class ConfigManager:
    @staticmethod
    def setup_config(api_key=None):
        """Set up configuration directory and save API key if provided"""
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

    @staticmethod
    def resolve_api_key():
        """Resolve API key from environment variable or config file, with user prompt as fallback"""
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

        ConfigManager.setup_config(api_key)
        return api_key