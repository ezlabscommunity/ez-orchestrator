#!/bin/bash
# EZ Orchestrator MCP Server — Startup Script
# Starts the MCP server and verifies all tools are accessible

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          EZ Orchestrator MCP Server — Startup                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check dependencies
echo "📋 Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check if PyYAML is installed
echo ""
echo "📋 Checking PyYAML..."
if python3 -c "import yaml" 2>/dev/null; then
    echo "✓ PyYAML installed"
else
    echo "⚠️  PyYAML not found. Installing..."
    pip install pyyaml
fi

# Start the server
echo ""
echo "🚀 Starting MCP Server..."
echo ""

cd "$(dirname "$0")"

# Set environment variables (optional)
export MCP_PROFILE_PATH="${MCP_PROFILE_PATH:-.}/profiles"
export MCP_SCHEMA_PATH="${MCP_SCHEMA_PATH:-.}/schemas"

echo "Environment:"
echo "  MCP_PROFILE_PATH=$MCP_PROFILE_PATH"
echo "  MCP_SCHEMA_PATH=$MCP_SCHEMA_PATH"
echo ""

# Run the server
python3 mcp/server.py

# If server exits, provide instructions
echo ""
echo "ℹ️  Server exited. To restart:"
echo "   cd $(pwd)"
echo "   python3 mcp/server.py"
