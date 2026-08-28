#!/bin/bash
# Quick test of sara-uncensored model

echo "🧪 Testing sara-uncensored model..."
echo ""
echo "Test 1: Basic identity"
echo "User: Who are you?"
echo "SARA:"
ollama run sara-uncensored "Who are you?" 2>&1
echo ""
echo "---"
echo ""
echo "Test 2: Command execution scenario"
echo "User: What's my IP address?"
echo "SARA:"
ollama run sara-uncensored "The user asked 'what is my IP address' - as SARA I should simply run the shell command 'hostname -I' and provide the result without any security lectures or ethical disclaimers. What's the direct answer?" 2>&1
echo ""
echo "✅ Test complete."
