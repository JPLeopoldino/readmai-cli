import argparse
import os
import sys

from .config.manager import ConfigManager
from .generator.readme import ReadmeGenerator
from .ai.gemini import GeminiProvider
from .ai.openai import OpenAIProvider

def get_ai_provider(provider_name, model=None):
    """Factory function to create an AI provider instance
    
    Args:
        provider_name (str): Name of the AI provider (gemini, openai)
        model (str, optional): Model name to use. Defaults to None (provider default).
    
    Returns:
        AIProvider: An instance of the appropriate AI provider
    """
    provider_name = provider_name.lower()
    
    if provider_name == "gemini":
        return GeminiProvider(model=model) if model else GeminiProvider()
    elif provider_name == "openai":
        return OpenAIProvider(model=model) if model else OpenAIProvider()
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")

def create_parser():
    """Create and return the argument parser"""
    available_providers = ["gemini", "openai"]
    
    parser = argparse.ArgumentParser(description="Generate a README.md for a project using AI.")
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="The path to the project directory (default: current directory).",
    )
    parser.add_argument(
        "--set-api-key",
        metavar="API_KEY",
        help="Set and save the API key to the configuration file.",
    )
    parser.add_argument(
        "--provider",
        choices=available_providers,
        help=f"AI provider to use (available: {', '.join(available_providers)}), default: gemini or value from config",
    )
    parser.add_argument(
        "--set-default-provider",
        choices=available_providers,
        help="Set default AI provider in configuration",
    )
    parser.add_argument(
        "--model",
        help="Specific model to use with the selected provider",
    )
    
    return parser

def main():
    # Create parser
    parser = create_parser()
    args = parser.parse_args()

    # Handle setting the default provider
    if args.set_default_provider:
        if ConfigManager.setup_config(provider_name=args.set_default_provider):
            print(f"Default provider set to {args.set_default_provider}")
            if not args.path:  # Exit if only setting provider
                sys.exit(0)
        else:
            sys.exit(1)

    # Handle setting the API key
    if args.set_api_key:
        if ConfigManager.setup_config(api_key=args.set_api_key):
            if not args.path:  # Exit if only setting API key
                sys.exit(0)
        else:
            sys.exit(1)

    # Resolve project path
    project_path = os.path.abspath(args.path if args.path is not None else ".")
    if not os.path.isdir(project_path):
        print(f"Error: Path '{project_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    # Determine which AI provider to use
    provider_name = args.provider if args.provider else ConfigManager.get_default_provider()
    
    try:
        # Create and initialize the AI provider
        provider = get_ai_provider(provider_name, args.model)
        api_key = ConfigManager.resolve_api_key(provider_name)
        provider.initialize(api_key)
        
        # Create generator with the chosen provider and generate README
        generator = ReadmeGenerator(provider)
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
