import httpx
import asyncio
from datetime import datetime
from monitor.detector import AnomalyDetector
from groq import Groq
import os
from dotenv import load_dotenv
from pathlib import Path

# Load env - works both locally and on Streamlit Cloud
try:
    import streamlit as st
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found.")

client = Groq(api_key=GROQ_API_KEY)

MONITORED_APIS = [
    {"name": "JSONPlaceholder Posts", "url": "https://jsonplaceholder.typicode.com/posts/1"},
    {"name": "JSONPlaceholder Users", "url": "https://jsonplaceholder.typicode.com/users/1"},
    {"name": "HTTPBin Status", "url": "https://httpbin.org/status/200"},
    {"name": "HTTPBin Delay", "url": "https://httpbin.org/delay/1"},
    {"name": "HTTPBin Slow API", "url": "https://httpbin.org/delay/3"},
    {"name": "Failing API Simulation", "url": "https://httpbin.org/status/500"},
]

detectors = {api["name"]: AnomalyDetector() for api in MONITORED_APIS}
alerts = []
api_logs = {api["name"]: [] for api in MONITORED_APIS}

async def check_api(api):
    name = api["name"]
    url = api["url"]
    start = asyncio.get_event_loop().time()
    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            response = await client_http.get(url)
            response_time = round((asyncio.get_event_loop().time() - start) * 1000, 2)
            status_code = response.status_code
    except Exception:
        response_time = 9999
        status_code = 500

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "response_time": response_time,
        "status_code": status_code,
        "is_anomaly": False
    }

    detector = detectors[name]
    detector.add_sample(response_time, status_code)
    detector.train()

    is_anomaly = detector.predict(response_time, status_code)
    log_entry["is_anomaly"] = is_anomaly

    api_logs[name].append(log_entry)

    if len(api_logs[name]) > 50:
        api_logs[name] = api_logs[name][-50:]

    if is_anomaly:
        explanation = generate_explanation(name, response_time, status_code)
        alert = {
            "timestamp": datetime.now().isoformat(),
            "api_name": name,
            "response_time": response_time,
            "status_code": status_code,
            "explanation": explanation
        }
        alerts.append(alert)
        if len(alerts) > 20:
            alerts.pop(0)

    return log_entry

def generate_explanation(api_name, response_time, status_code):
    try:
        prompt = f"""You are an expert SRE engineer. An API anomaly was detected.

API: {api_name}
Response Time: {response_time}ms
Status Code: {status_code}

In 2-3 sentences explain:
1. What likely went wrong
2. One specific debugging step to take immediately

Be direct and technical."""

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Anomaly detected — response time {response_time}ms with status {status_code}. Check server logs immediately."

async def run_monitoring():
    while True:
        tasks = [check_api(api) for api in MONITORED_APIS]
        await asyncio.gather(*tasks)
        await asyncio.sleep(15)

def get_alerts():
    return alerts

def get_logs():
    return api_logs

def get_stats():
    return {
        name: detectors[name].get_stats()
        for name in detectors
    }