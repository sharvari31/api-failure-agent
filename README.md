API Failure Detection & Debugging Agent
An AI-powered agent that monitors API endpoints, detects failures and latency anomalies, identifies patterns, and generates plain-English debugging recommendations automatically.
Problem It Solves
Engineering teams often discover API failures only after users complain. Silent failures, latency spikes, and recurring errors go unnoticed until they cause real damage. This agent monitors continuously and explains what went wrong before users notice.
Features-
Real-time API endpoint monitoring
Anomaly detection on response times and failure rates
AI-generated plain English explanation of failures
Debugging recommendations with likely root causes
Live dashboard showing API health status
Automatic alerts when failures are detected


Tech Stack-
Python, FastAPI
Scikit-learn — Isolation Forest for anomaly detection
OpenAI API — for generating debugging explanations
Streamlit — frontend dashboard
Docker — containerised deployment
Python, FastAPI
Scikit-learn — Isolation Forest for anomaly detection
OpenAI API — for generating debugging explanations
Streamlit — frontend dashboard
Docker — containerised deployment

How It Works

Agent continuously pings monitored API endpoints
Collects response time, status codes, and error messages
Isolation Forest model detects anomalous behaviour
LLM generates human readable explanation and fix recommendations
Dashboard displays real time health and alert history

Demo
[Link to demo video]
