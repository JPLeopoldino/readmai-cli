import os
import sys
from halo import Halo

from ..scanner.project import ProjectScanner
from ..utils.markdown import MarkdownUtils
from ..ai.provider import AIProvider

class ReadmeGenerator:
    def __init__(self, ai_provider):
        """Initialize the README generator with the given AI provider
        
        Args:
            ai_provider (AIProvider): An initialized AI provider
        """
        if not isinstance(ai_provider, AIProvider):
            raise TypeError("ai_provider must be an instance of AIProvider")
        self.provider = ai_provider
    
    def generate(self, project_path):
        """Generate a README.md file for the given project path"""
        spinner = None
        
        try:
            project_structure = ProjectScanner.scan_structure(project_path)
            if not project_structure:
                print("Could not find any relevant files in the project path.", file=sys.stderr)
                return False

            prompt = self._create_prompt(project_structure)
            spinner = Halo(text=f'Generating README with {self.provider.name}', spinner='dots')
            spinner.start()
            
            content = self.provider.generate_content(prompt)
            spinner.succeed('README content generated.')

            if not content:
                print(f"\nError: {self.provider.name} returned an empty response.", file=sys.stderr)
                return False

            readme_content = MarkdownUtils.clean_code_blocks(content)
            readme_path = os.path.join(project_path, "README.md")
            
            print(f"Writing README.md to: {readme_path}")
            with open(readme_path, "w") as f:
                f.write(readme_content)
            print("README.md generated successfully.")
            return True

        except Exception as e:
            if spinner:
                spinner.fail(f'Generation failed: {e}')
            else:
                print(f"\nError generating README: {e}", file=sys.stderr)
            return False
        finally:
            if spinner:
                spinner.stop()
    
    def _create_prompt(self, project_structure):
        """Create the prompt for the AI model"""
        return f"""
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