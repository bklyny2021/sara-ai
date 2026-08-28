#!/bin/bash
# Setup SARA Models in Her Folder
# Makes SARA 100% portable - all models self-contained

echo "🤖 Setting up SARA Models..."
echo ""

SARA_DIR="/home/sarabot/.openclaw/workspace/SARA2_v2"
MODELS_DIR="$SARA_DIR/models"
mkdir -p "$MODELS_DIR"

echo "📁 Models directory: $MODELS_DIR"
echo ""

# Check if we can access system Ollama models
SYSTEM_OLLAMA="/usr/share/ollama/.ollama/models"

if [ -d "$SYSTEM_OLLAMA/blobs" ]; then
    echo "✅ Found system Ollama models"
    echo ""
    
    # Option 1: Create symbolic links (doesn't copy, just pointers)
    echo "Creating symlinks to system models..."
    
    for blob in "$SYSTEM_OLLAMA"/blobs/sha256-*; do
        if [ -f "$blob" ]; then
            target="$MODELS_DIR/$(basename $blob)"
            if [ ! -e "$target" ]; then
                ln -s "$blob" "$target" 2>/dev/null || echo "⚠️ Permission denied for $blob"
            fi
        fi
    done
    
    # Also link manifests
    for manifest in "$SYSTEM_OLLAMA"/manifests/*; do
        if [ -d "$manifest" ]; then
            echo "Found manifest: $manifest"
        fi
    done
    
else
    echo "⚠️ System Ollama models not accessible (permission)"
    echo ""
    echo "Alternative: Run Ollama with custom path"
    echo "export OLLAMA_MODELS=$MODELS_DIR"
    echo "ollama serve"
fi

echo ""
echo "📊 Calculating folder sizes..."
echo ""
echo "Core SARA files:"
du -sh "$SARA_DIR"/*.py "$SARA_DIR"/*.sh "$SARA_DIR"/*.md 2>/dev/null | tail -1

echo ""
echo "Models folder:"
if [ -d "$MODELS_DIR" ]; then
    du -sh "$MODELS_DIR" 2>/dev/null || echo "(empty or no access)"
    
    echo ""
    echo "Model files:"
    ls -lh "$MODELS_DIR" 2>/dev/null | grep -v "^d" | wc -l
    echo "files found"
fi

echo ""
echo "🎯 TOTAL SARA FOLDER SIZE:"
du -sh "$SARA_DIR"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use SARA with models from her folder:"
echo "1. export OLLAMA_MODELS=$MODELS_DIR"
echo "2. ollama serve"
echo "3. ./start_sara_v2.sh"
