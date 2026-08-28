#!/bin/bash
cd /home/sarabot/.openclaw/workspace/SARA2_v2
pkill -9 -f sara_web 2>/dev/null
sleep 2
python3 sara_web_fixed.py &
sleep 5
curl -s -X POST http://127.0.0.1:8892/ask -H "Content-Type: application/json" -d '{"question":"What is the IP pool on this PC?"}'