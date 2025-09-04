#!/bin/bash

# Invoice Generator Runner Script
# This script sets up the environment and runs the invoice generator

echo "🧾 Invoice Generator Setup & Runner"
echo "=================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run the invoice generator
echo "🚀 Running invoice generator..."
python simple_generator.py

echo ""
echo "✅ Done! Check the 'generated_invoices' folder for your PDF files."
echo "📋 HTML previews are also available for browser viewing."
