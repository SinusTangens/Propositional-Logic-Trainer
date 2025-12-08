#!/bin/bash

# This script sets up the project from scratch using uv

# ---------------------------------------------------------
# Load Python version from .python-version
# ---------------------------------------------------------
if [ ! -f ".python-version" ]; then
    echo " .python-version file not found!"
    echo "Bitte lege eine Datei '.python-version' im Projektverzeichnis an."
    exit 1
fi

# Read the version and trim whitespace/newlines
PYTHON_VERSION=$(cat .python-version | tr -d '[:space:]')

echo ">>> Using Python version $PYTHON_VERSION"


# ---------------------------------------------------------
# Install Python version via uv
# ---------------------------------------------------------
echo ">>> Installing Python version $PYTHON_VERSION"
uv python install "$PYTHON_VERSION"

# ---------------------------------------------------------
# Remove any existing virtual environment
# ---------------------------------------------------------
echo ">>> Removing existing virtual environment (if present)"
rm -rf .venv

# ---------------------------------------------------------
# Pin Python version for this project & create venv
# ---------------------------------------------------------
echo ">>> Pinning python version"
uv python pin "$PYTHON_VERSION"

echo ">>> Creating fresh virtual environment"
uv venv --python "$PYTHON_VERSION"

# ---------------------------------------------------------
# Activate the virtual environment (delegated to activate.sh)
# ---------------------------------------------------------
echo ">>> Activating virtual environment..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # MacOS or Linux
    source .venv/bin/activate
fi

# ---------------------------------------------------------
# Install dependencies from requirements.txt
# ---------------------------------------------------------
echo ">>> Installing project dependencies"
uv pip install --overrides requirements.txt -r requirements.txt

# ---------------------------------------------------------
# Remove uv lock file (project uses requirements.txt, not uv.lock)
# ---------------------------------------------------------
echo ">>> Removing uv lock files (if any)"
rm -f uv.lock

echo -e "\033[0;32m Setup erfolgreich abgeschlossen!\033[0m"





