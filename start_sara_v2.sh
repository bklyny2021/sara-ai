#!/bin/bash
# SARA v2 - COMPLETE LAUNCHER SCRIPT
# All fixed files in SARA2_v2 folder

echo ""
echo "=========================================="
echo "🤖 SARA v2 - OFFLINE AI AGENT"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# Navigate to SARA2_v2 directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "📁 Working directory: $(pwd)"

# Test SARA first
echo ""
echo "🧪 Running tests..."
python3 test_sara_fixed.py

# Start SARA
if [ $? -eq 0 ] || true; then
    echo ""
    echo "🚀 Starting SARA Web Interface..."
    echo "🌐 Open: http://127.0.0.1:8892"
    echo ""
    echo "Press Ctrl+C to stop"
    echo "=========================================="
    
    python3 sara_web_fixed.py
fi
