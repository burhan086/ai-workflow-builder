🛡️ AI Workflow Builder: Natural Language to Executable Pipelines

An agentic automation platform that translates plain English instructions into structured, executable API pipelines. By combining LLM orchestration with a dynamic execution engine, this tool allows users to build complex cross-platform workflows (GitHub, Discord, Slack) without writing a single line of code.

![alt text](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)


![alt text](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)


![alt text](https://img.shields.io/badge/Llama_3.3-Groq-orange?style=for-the-badge)

🚀 Key Features

Natural Language Understanding: Uses Llama-3.3-70B to parse unstructured user intent into structured JSON execution plans.

Dynamic DAG Generation: Automatically constructs a Directed Acyclic Graph (DAG) to visualize data dependencies between tasks.

Agentic Reasoning: The AI identifies which tools are necessary, extracts required parameters (like repository names or messages), and handles sequence chaining.

Live Integrations:

GitHub API: Fetches real-time commit data and repository metadata.

Notification Webhooks: Dispatches automated updates to Discord or Slack.

Secure Architecture: Implements environment-based credential management to ensure API security.

🧠 How It Works

The system follows a "Brain & Hands" architecture:

The Brain (Reasoning Layer): The LLM receives the user prompt and decides which tools to call. It outputs a JSON schema defining the sequence and data flow (e.g., Step 1 output -> Step 2 input).

The Execution Engine (Action Layer): A Python-based dispatcher executes the tools in order, injecting data dependencies and handling API authentication.

The UI (Monitoring Layer): A Streamlit dashboard renders the pipeline graph and provides real-time execution logs.

🛠️ Tech Stack

LLM Orchestration: Groq Cloud (Llama 3.3 70B Versatile)

Framework: Streamlit (UI), Pydantic (Data Validation)

Visualizations: Graphviz (DAG Rendering)

API Handling: Requests (GitHub REST API, Discord Webhooks)

DevOps: Docker, Python-Dotenv

📦 Installation & Setup

Clone the repository:

code
Bash
download
content_copy
expand_less
git clone https://github.com/YOUR_USERNAME/ai-workflow-builder.git
cd ai-workflow-builder

Install dependencies:

code
Bash
download
content_copy
expand_less
pip install -r requirements.txt

Configure Environment Variables:
Create a .env file in the root directory:

code
Text
download
content_copy
expand_less
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_pat
NOTIFICATION_WEBHOOK=your_discord_or_slack_webhook_url

Run the application:

code
Bash
download
content_copy
expand_less
streamlit run app.py
📝 Example Workflows to Try

Full Pipeline: "Fetch the latest commits from tensorflow/tensorflow, summarize them using AI, and post the summary to Discord."

Direct Action: "Send a notification to my team saying: 'The server maintenance is complete'."

Custom Style: "Summarize the updates in microsoft/vscode in the style of a pirate and alert the channel."

📊 System Architecture
code
Mermaid
download
content_copy
expand_less
graph TD
    A[User Prompt] --> B{LLM Optimizer}
    B -->|JSON Schema| C[Execution Engine]
    C --> D[GitHub Tool]
    C --> E[AI Summarizer]
    C --> F[Discord/Slack Tool]
    D --> E
    E --> F
    F --> G[End User]
    
🛡️ Future Roadmap

Self-Healing Workflows: Add a feedback loop where the AI fixes the pipeline if an API returns an error.

Multi-Tool Selection: Allow the AI to choose between Email, Slack, or Discord based on urgency.

Vector Search (RAG): Integrate a vector database to allow the AI to search through internal documentation before sending notifications.


⚠️ Security Note

This project uses .env files for secret management. Ensure that your .env is added to your .gitignore before pushing to public repositories.

