import os
import sys
import configparser
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "readmai"
CONFIG_FILE = CONFIG_DIR / "config.ini"

class ConfigManager:
    @staticmethod
    def setup_config(api_key=None, provider_name=None):
        """Set up configuration directory and save API key if provided"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        config = configparser.ConfigParser()
        if CONFIG_FILE.exists():
            config.read(CONFIG_FILE)
        
        if "Credentials" not in config:
            config["Credentials"] = {}
            
        if "Settings" not in config:
            config["Settings"] = {}
        
        # Save provider preference if specified
        if provider_name:
            config["Settings"]["default_provider"] = provider_name
            
        # Save API key if specified
        if api_key:
            config["Credentials"]["api_key"] = api_key
            
        # Only write if we have changes to save
        if api_key or provider_name:
            try:
                with open(CONFIG_FILE, "w") as configfile:
                    config.write(configfile)
                os.chmod(CONFIG_FILE, 0o600)
                
                if api_key:
                    print(f"API key saved to {CONFIG_FILE}")
                if provider_name:
                    print(f"Default AI provider set to {provider_name}")
                    
                return True
            except IOError as e:
                print(f"Error saving configuration to {CONFIG_FILE}: {e}", file=sys.stderr)
                return False
        return True

    @staticmethod
    def get_default_provider():
        """Get default AI provider from config, defaults to 'gemini' if not specified"""
        if CONFIG_FILE.exists():
            config = configparser.ConfigParser()
            try:
                config.read(CONFIG_FILE)
                return config.get("Settings", "default_provider", fallback="gemini")
            except Exception:
                pass
        return "gemini"

    @staticmethod
    def resolve_api_key(provider="gemini"):
        """Resolve API key from environment variable or config file, with user prompt as fallback"""
        env_var_name = f"{provider.upper()}_API_KEY"
        api_key = os.environ.get(env_var_name)
        if api_key:
            print(f"Using API key from {env_var_name} environment variable.")
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

        api_key = input(f"Please enter your {provider.capitalize()} API key: ").strip()
        if not api_key:
            print("No API key provided. Exiting.", file=sys.stderr)
            sys.exit(1)

        ConfigManager.setup_config(api_key)
        return api_key