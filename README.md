# readmai-cli

This project is a command-line interface (CLI) application named `readmai-cli`. It consists of a Python package named `readmai` with a CLI entry point defined in `readmai/cli.py`. The `readmai-cli` directory serves as the packaging and distribution directory for the CLI application.

## Installation

1.  Ensure you have Python and `pip` installed.
2.  Navigate to the `readmai-cli` directory:

    ```bash
    cd readmai-cli
    ```

3.  Create a virtual environment (recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate  # On Windows
    ```

4.  Install the package and its dependencies:

    ```bash
    pip install .
    ```
    Alternatively, you may install dependencies specified in `requirements.txt` first and then install the package.

    ```bash
    pip install -r requirements.txt
    pip install .
    ```

    Installation also works by installing the `readmai` package directly, which `readmai_cli` depends on, using pip.
    ```bash
    cd src
    pip install .
    ```
## Usage

After installation, you should be able to run the `readmai` command from your terminal.

```bash
readmai --help  # To see available options
```

The specific commands and options available depend on the implementation in `readmai/cli.py`. Refer to that file or use the `--help` flag to understand the CLI's functionality.

## Project Structure

The project directory structure is organized as follows:

-   `readmai-cli/`: The top-level directory for the CLI distribution.
    -   `requirements.txt`: Specifies the Python package dependencies.
    -   `pyproject.toml`: Configuration file for building the project (likely contains build system settings, package metadata, etc.).
    -   `src/`: Contains the source code of the project.
        -   `readmai_cli.egg-info/`: Metadata directory generated during the building of the `readmai-cli` package.  Contains information like dependencies, entry points, and package versions.
        -   `readmai/`: Contains the Python package `readmai`.
            -   `__init__.py`: Makes the directory a Python package.
            -   `cli.py`: Contains the implementation of the command-line interface. This likely uses a library such as `argparse` or `click`.
        -   `readmai.egg-info/`: Metadata directory generated during the building of the `readmai` package. Contains information like dependencies, entry points, and package versions.

## Metadata Files

The `*.egg-info` directories contain various metadata files:

-   `PKG-INFO`: Package metadata (name, version, description, etc.).
-   `SOURCES.txt`: List of all source files included in the package.
-   `entry_points.txt`: Defines command-line entry points (likely used to make `readmai` executable).
-   `top_level.txt`: Specifies the top-level packages or modules included in the distribution.
-   `dependency_links.txt`: Lists URLs for package dependencies.