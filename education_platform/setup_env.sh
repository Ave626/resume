#!/bin/bash
# Exit on error
set -e

echo "Creating virtual environment in .venv..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements from requirements.txt..."
pip install -r requirements.txt

echo "Setup completed successfully!"
echo "To activate the environment, run:"
echo "  source .venv/bin/activate"
