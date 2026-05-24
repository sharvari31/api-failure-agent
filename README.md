# API Failure Detection & Debugging Agent

An AI-powered agent that monitors API endpoints in real-time, detects anomalies using machine learning, and generates plain-English debugging recommendations automatically.

## Problem It Solves
Engineering teams discover API failures only after users complain. Silent failures, latency spikes, and 500 errors go unnoticed until real damage is done. This agent monitors continuously and explains what went wrong before users notice.

## Features
- Real-time monitoring of multiple API endpoints
- Anomaly detection using Isolation Forest ML algorithm
- AI-generated debugging recommendations via Groq LLaMA3
- Live dashboard with response time charts
- Automatic anomaly alerts with root cause analysis
- Color coded API health status — Healthy, Warning, Critical

## Tech Stack
- Python
- Scikit-learn — Isolation Forest for anomaly detection
- Groq LLaMA3 — AI generated debugging explanations
- Streamlit — live dashboard frontend
- Httpx — async API monitoring
- APScheduler — scheduled monitoring tasks

## How It Works
1. Agent continuously pings monitored API endpoints every 15 seconds
2. Collects response time and status codes
3. Isolation Forest ML model detects anomalous behaviour
4. Groq LLaMA3 generates plain English explanation and fix recommendations
5. Dashboard displays real time health status and alert history

## Setup

```bash
pip install -r requirements.txt
```

Create a .env file:
