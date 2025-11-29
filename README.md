# Smart Order Issue Support Agent

## Project Description
This AI-driven "Smart Order Issue Support Agent" is a sophisticated platform engineered to intelligently manage a diverse range of customer order issues. 
Leveraging cutting-edge multi-modal AI capabilities, it seamlessly processes various input types, including detailed images for damage detection and classification. 
Its robust architecture features specialized agents that utilize powerful vision models to accurately assess damage type, severity, and derive comprehensive analysis directly from uploaded images.
The system adeptly handles multiple use cases, from damaged items to not-delivered orders, and intelligently orchestrates workflows, including agents invoking other agents as tools, to provide precise resolutions, integrate relevant policy information, and ensure superior customer satisfaction.

## Features
- **Multi-modal Input Processing**: Accepts both text and image inputs for comprehensive issue understanding.
- **AI-Powered Damage Detection**: Utilizes advanced AI vision models to analyze uploaded images for damage type, severity, and affected areas without simulation.
- **Diverse Use Case Handling**: Supports workflows for damaged items and not-delivered orders.
- **Agent Orchestration**: Intelligent agents can invoke other specialized agents and tools to resolve complex issues.
- **Policy Integration**: Provides relevant policy information (e.g., warranty, return policy) based on issue analysis.
- **Structured Damage Reports**: Generates detailed, actionable reports for customer service.
- **Scalable and Resumable**: Built with Google ADK for scalable and resumable agent interactions.

## Setup Instructions

### Prerequisites
- Python 3.9+
- Google Cloud Project with Gemini API enabled (for AI Vision capabilities)
- `pip` for package installation

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [repository_url]
    cd smart-order-issue-support-agent
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
      google-generativeai
      google-adk
      chromadb
      python-dotenv

5.  **Configure Environment Variables:**
    Create a `.env` file in the project root and add your Google API Key:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```

## Usage

To run the main application:
```bash
adk web --session_service_uri sqlite:///my_agent_data.db --log_level=debug
```

Interact with the agents to process order issues. For damaged items, provide an image  when prompted.

---
```

I'm ready to create this `README.md` file. Please switch to Act mode when you're ready for me to proceed.
