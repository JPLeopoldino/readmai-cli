import os
from halo import Halo

class ProjectScanner:
    @staticmethod
    def scan_structure(path):
        """Scan project directory structure and return a formatted string representation"""
        structure = []
        spinner = Halo(text='Scanning project structure...', spinner='dots')
        
        try:
            spinner.start()
            for root, dirs, files in os.walk(path):
                # Filter out hidden and common build directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                           d not in ['node_modules', 'venv', '.venv', '__pycache__', 
                                    'build', 'dist', '.git']]
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
            if spinner:
                spinner.stop()
            
        return "\n".join(structure)