# Readmai-CLI

Readmai-CLI is a command-line tool designed to automatically generate README files for software projects using AI. Based on the project's structure, it utilizes AI providers to create descriptive and informative README files.

## Project Structure

The project has the following directory structure:

```
readmai-cli/
    requirements.txt
    pyproject.toml
    README.md
    src/
        readmai_cli.egg-info/
            PKG-INFO
            SOURCES.txt
            entry_points.txt
            top_level.txt
            dependency_links.txt
        readmai/
            __init__.py
            cli.py
            config/
                __init__.py
                manager.py
            utils/
                __init__.py
                markdown.py
            generator/
                readme.py
                __init__.py
            ai/
                provider.py
                __init__.py
                gemini.py
                openai.py
            scanner/
                __init__.py
                project.py
        readmai.egg-info/
            PKG-INFO
            SOURCES.txt
            entry_points.txt
            top_level.txt
            dependency_links.txt
```

This structure indicates:

*   The `readmai` package contains the core logic of the application.
*   `cli.py` likely serves as the command-line interface entry point.
*   The `config` directory manages application configuration.
*   The `utils` directory provides utility functions, including Markdown processing.
*   The `generator` directory handles the creation of README files.
*   The `ai` directory integrates with AI providers like Gemini and OpenAI to generate README content. `provider.py` provides an abstraction layer for different AI providers.
*   The `scanner` directory includes project scanning functionalities, likely to analyze project structure for the AI to consume.
*   `requirements.txt` and `pyproject.toml` manage project dependencies and build configuration.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd readmai-cli
    ```

2.  **Install dependencies:**

    Using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

    or, using `poetry` or `pipenv` as defined by `pyproject.toml`:

    ```bash
    # Example using Poetry
    poetry install
    ```
    or
    ```bash
    # Example using pipenv
    pipenv install
    ```

## Usage

The project includes a `cli.py` file, suggesting it's a command-line tool.  You can likely execute it as follows:

1.  **Run the CLI:**

    If installed with pip directly:

    ```bash
    readmai --help  # (Example command - replace with actual command-line options)
    ```

    If using `poetry`:

    ```bash
    poetry run readmai --help # (Example command - replace with actual command-line options)
    ```
    If using `pipenv`:

    ```bash
    pipenv run readmai --help # (Example command - replace with actual command-line options)
    ```

    The `--help` flag should display available commands and options. Replace `<repository_url>` and update the example commands with the actual usage instructions.

2.  **Generate a README:**

    You may need to configure the AI provider using the `config` directory. Then, you can run the generation command.

    ```bash
    readmai generate  # (Example command - replace with actual command-line options)
    ```

## Configuration

The `config` directory indicates that you can configure the application.  Check the `config/manager.py` file for details on configuration options. You might be able to set API keys for the AI providers (Gemini, OpenAI) via configuration files or environment variables. Details will be in `config/manager.py`.

## AI Providers

The `ai` directory supports AI providers such as Gemini and OpenAI. Ensure you have the necessary API keys and configure them correctly using the configuration instructions to utilize these providers. The `provider.py` suggests a generic AI interface allowing you to easily switch between AI services.

## Contributions

Contributions are welcome! Please submit pull requests with detailed descriptions of your changes.