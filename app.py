import streamlit as st
import json
import os
import requests
import graphviz
from groq import Groq
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Production AI Workflow", layout="wide")

GROQ_KEY = os.getenv("GROQ_API_KEY")
GH_TOKEN = os.getenv("GITHUB_TOKEN")
WEBHOOK_URL = os.getenv("NOTIFICATION_WEBHOOK")

client = Groq(api_key=GROQ_KEY)

# --- 2. THE REAL TOOLS ---

def github_fetch(repo_name):
    """Fetches real commit messages from a public or private GitHub repo."""
    # If repo_name is not provided by AI, use a default for testing
    if not repo_name or repo_name == "default":
        repo_name = "tensorflow/tensorflow" # Example public repo
    
    url = f"https://api.github.com/repos/{repo_name}/commits?per_page=5"
    headers = {"Authorization": f"token {GH_TOKEN}"} if GH_TOKEN else {}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            msgs = [c['commit']['message'] for c in commits]
            return f"Raw Commits from {repo_name}: " + " | ".join(msgs)
        else:
            return f"GitHub Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"GitHub Connection Failed: {str(e)}"

def llm_summarize(text_to_summarize):
    """Uses AI to actually summarize the raw data fetched from GitHub."""
    if not text_to_summarize:
        return "No text provided to summarize."
        
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a technical writer. Summarize these git commits into a single punchy sentence for a team update."},
                {"role": "user", "content": text_to_summarize}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Summarization Error: {str(e)}"

def send_notification(message):
    """Sends a real message to Discord or Slack."""
    if not WEBHOOK_URL:
        return "Notification skipped: No Webhook URL found in .env"
    
    # Payload for Discord (uses 'content') or Slack (uses 'text')
    payload = {"content": message} if "discord.com" in WEBHOOK_URL else {"text": message}
    
    try:
        res = requests.post(WEBHOOK_URL, json=payload)
        if res.status_code in [200, 204]:
            return "🚀 Success! Notification sent to the live channel."
        else:
            return f"Webhook Failed: {res.status_code}"
    except Exception as e:
        return f"Notification Error: {str(e)}"

# --- 3. THE DISPATCHER (Engine) ---

def execute_tool(tool_name, input_val, repo_arg="default"):
    if tool_name == "github_fetch": return github_fetch(repo_arg)
    if tool_name == "llm_summarize": return llm_summarize(input_val)
    if tool_name == "send_notification": return send_notification(input_val)
    return "Unknown Tool"

# --- 4. AI AGENT LOGIC ---

def generate_workflow(user_prompt):
    system_prompt = """
    Convert user request into a JSON workflow.
    Tools: 
    - github_fetch (args: repo_name)
    - llm_summarize (needs input from github)
    - send_notification (needs input from summarize)
    
    Output JSON ONLY: {"steps": [{"step_id": 1, "tool": "tool_name", "input_from_step": null, "repo_name": "user/repo"}]}
    """
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

# --- 5. UI ---

st.title("🛡️ Production AI Workflow Builder")
st.info("Status: " + ("Connected to APIs" if WEBHOOK_URL and GH_TOKEN else "Running in Semi-Mock Mode (Check .env)"))

user_input = st.text_input("Describe your automation:", placeholder="e.g., Fetch commits from openai/whisper, summarize them, and notify my team.")

if user_input:
    # 1. Reasoning Phase
    with st.spinner("AI is planning the pipeline..."):
        workflow = generate_workflow(user_input)
    
    # 2. Visual Phase
    dot = graphviz.Digraph()
    for s in workflow['steps']:
        dot.node(str(s['step_id']), f"{s['tool']}")
        if s.get('input_from_step'):
            dot.edge(str(s['input_from_step']), str(s['step_id']))
    st.graphviz_chart(dot)

    # 3. Execution Phase
    if st.button("Execute Live Workflow"):
        results = {}
        for s in workflow['steps']:
            with st.status(f"Running {s['tool']}...") as status:
                prev_out = results.get(s.get('input_from_step'), "")
                repo = s.get('repo_name', 'default')
                
                output = execute_tool(s['tool'], prev_out, repo)
                results[s['step_id']] = output
                
                st.write(output)
                status.update(label=f"{s['tool']} Finished", state="complete")
        st.success("Workflow Complete!")