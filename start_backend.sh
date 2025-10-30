#!/bin/bash
echo "Starting CodeAssess Backend..."
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000