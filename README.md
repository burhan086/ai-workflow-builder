🛡️ AI Workflow Builder: Natural Language to Executable Pipelines

https://burhan-ai-workflow-builder.streamlit.app/


An agentic automation platform that translates plain English into structured API pipelines using **Llama-3.3-70B**.

## 🚀 Key Features
- **NLU Parsing:** Converts unstructured intent into JSON execution plans.
- **Dynamic DAGs:** Visualizes data dependencies via Graphviz.
- **Agentic Logic:** Identifies necessary tools (GitHub, AI, Discord) and chains them.

## 🛠️ Setup
1. `pip install -r requirements.txt`
2. Add API keys to `.env` (Groq, GitHub, Discord Webhook).
3. `streamlit run app.py`

## 📊 Architecture
```mermaid
graph TD
    A[User Prompt] --> B{LLM Planner}
    B --> C[Execution Engine]
    C --> D[GitHub Tool]
    D --> E[AI Summarizer]
    E --> F[Discord/Slack]
