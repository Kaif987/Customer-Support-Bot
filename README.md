# Customer Support Bot 🤖

This repository hosts a [Customer Support Bot](https://langchain-ai.github.io/langgraph/tutorials/customer-support/customer-support/) built using **Streamlit**, **FastAPI**, and **LangGraph**. The bot can answer queries regarding Flight booking, Hotel Booking, Excursion and Car rental services. It also has access to tools to lookup policies, make sensitive changes like book a car, or a hotel. This repository is built on top of [Agent Service Toolkit](https://github.com/JoshuaC215/agent-service-toolkit) which provides a great starting point for building this agent.

### [Try the app!](https://customer-support-bot-1.onrender.com/) 
*(This is hosted on a free tier on render so this may take a while to load)*
![Agent Demo GIF](https://i.imgur.com/L8L7I0C.gif)

## Features

- **Streaming Support**: The response from agent can be streamed as token chunks or messages as per user preference
- **ToolCalling Support**: The agent can call tools to answer customer queries.
- **Human in the Loop Architechture**: The customer support bot asks for the users permission before calling a sensitive tool like booking a hotel for the user.
- **Asynchronous Design**: Utilizes async/await for efficient handling of concurrent requests.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Kaif987/Customer-Support-Bot.git
   ```

2. Setup environment variables and install dependencies:

   ```bash
      # At least one LLM API key is required
      echo 'OPENAI_API_KEY=your_openai_api_key' >> .env

      # uv is recommended but "pip install ." also works
      pip install uv
      uv sync --frozen
      # "uv sync" creates .venv automatically
      source .venv/bin/activate
   ```

3. Start the backend service:

   ```bash
      python src/run_service.py
   ```

4. Start the frontend service:

   ```bash
      # In another shell
      source .venv/bin/activate
      streamlit run src/streamlit_app.py
   ```

## Graph Image
![Customer Support](https://i.imgur.com/mU8Luyk.jpeg)
