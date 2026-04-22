import streamlit as st
import json
import os
import requests
import graphviz
from groq import Groq
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AI Workflow Builder Pro", layout="wide", page_icon="🛡️")

# Fetch API Keys from .env
GROQ_KEY = os.getenv("GROQ_API_KEY")
GH_TOKEN = os.getenv("GITHUB_TOKEN")
WEBHOOK_URL = os.getenv("NOTIFICATION_WEBHOOK")

# Initialize AI Client
client = Groq(api_key=GROQ_KEY)

# --- 2. THE REAL TOOLS (Action Layer) ---

def github_fetch(repo_name):
    """Fetches real commit messages from GitHub."""
    if not repo_name or repo_name == "default":
        return "Error: No repository name provided."
    
    url = f"https://api.github.com/repos/{repo_name}/commits?per_page=5"
    headers = {"Authorization": f"token {GH_TOKEN}"} if GH_TOKEN else {}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            msgs = [c['commit']['message'] for c in commits]
            return f"Raw Commits from {repo_name}: " + " | ".join(msgs)
        else:
            return f"GitHub Error: {response.status_code} (Check repo name or token)"
    except Exception as e:
        return f"GitHub Connection Failed: {str(e)}"

def llm_summarize(text_to_summarize):
    """Uses AI to summarize raw data into a professional update."""
    if not text_to_summarize or len(text_to_summarize) < 5:
        return "No sufficient content to summarize."
        
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Summarize these git commits into a single punchy sentence for a team update. Use a professional tone."},
                {"role": "user", "content": text_to_summarize}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Summarization Error: {str(e)}"

def send_notification(message):
    """Sends a real message to Discord or Slack."""
    if not WEBHOOK_URL:
        return "Notification skipped: No Webhook URL found in secrets."
    if not message:
        return "Error: Cannot send an empty message."
    
    # Payload for Discord ('content') or Slack ('text')
    payload = {"content": message} if "discord.com" in WEBHOOK_URL else {"text": message}
    
    try:
        res = requests.post(WEBHOOK_URL, json=payload)
        if res.status_code in [200, 204]:
            return f"🚀 Successfully sent: {message}"
        else:
            return f"Webhook Failed: {res.status_code}"
    except Exception as e:
        return f"Notification Error: {str(e)}"

# --- 3. THE DISPATCHER ---

def execute_tool(tool_name, input_val, repo_arg="default"):
    if tool_name == "github_fetch": return github_fetch(repo_arg)
    if tool_name == "llm_summarize": return llm_summarize(input_val)
    if tool_name == "send_notification": return send_notification(input_val)
    return f"Unknown Tool: {tool_name}"

# --- 4. AI AGENT LOGIC (Reasoning Layer) ---

def generate_workflow(user_prompt):
    system_prompt = """
    Convert user request into a JSON workflow.
    Available Tools: 
    1. github_fetch (args: repo_name) -> Fetches data.
    2. llm_summarize (needs input from github) -> Processes text.
    3. send_notification (needs input from summarize OR a direct static_message) -> Sends alerts.
    
    Output JSON ONLY. Format:
    {
        "steps": [
            {
                "step_id": 1, 
                "tool": "tool_name", 
                "input_from_step": null or ID, 
                "repo_name": "owner/repo",
                "static_message": "Use this if the user wants to send a specific message directly"
            }
        ]
    }
    """
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)

# --- 5. STREAMLIT UI ---

st.title("🛡️ Production AI Workflow Builder")
st.markdown("---")

# Status Indicators
col1, col2 = st.columns(2)
with col1:
    st.write("**System Status:**")
    if GROQ_KEY and WEBHOOK_URL:
        st.success("✅ Connected to APIs & Webhooks")
    else:
        st.warning("⚠️ Missing API Keys in .env")

# User Input Section
user_input = st.text_input("Describe your automation:", placeholder="e.g., Send a notification saying 'Server is down'...")

if user_input:
    # Phase 1: Planning
    with st.spinner("AI is designing the execution plan..."):
        workflow = generate_workflow(user_input)
    
    # Phase 2: Visualizing the DAG
    st.subheader("📊 Pipeline Architecture")
    dot = graphviz.Digraph()
    for s in workflow['steps']:
        dot.node(str(s['step_id']), f"{s['tool']}")
        if s.get('input_from_step'):
            dot.edge(str(s['input_from_step']), str(s['step_id']))
    st.graphviz_chart(dot)

    # Phase 3: Execution
    if st.button("🚀 Run Live Workflow"):
        st.subheader("⚙️ Execution Logs")
        results = {}
        
        for s in workflow['steps']:
            with st.status(f"Executing: {s['tool']}...") as status:
                # Resolve Input: Priority to previous step output, then static message
                prev_out = results.get(s.get('input_from_step'), "")
                static_msg = s.get('static_message', "")
                
                final_input = prev_out if prev_out else static_msg
                repo = s.get('repo_name', 'default')
                
                # Run the actual tool
                output = execute_tool(s['tool'], final_input, repo)
                results[s['step_id']] = output
                
                st.write(f"**Result:** {output}")
                status.update(label=f"Done: {s['tool']}", state="complete")
        
        st.success("✅ Workflow Chain Completed Successfully")
