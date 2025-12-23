#!/bin/bash

# Local Development - Backend ve Frontend'i birlikte başlat

echo "🚀 Starting Backend and Frontend..."

# Backend'i arka planda başlat
echo "📡 Starting Backend on http://localhost:8000"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# 3 saniye bekle (backend başlasın)
sleep 3

# Frontend'i başlat
echo "🎨 Starting Frontend on http://localhost:8501"
streamlit run app.py

# Script sonlandığında backend'i de kapat
trap "kill $BACKEND_PID" EXIT

