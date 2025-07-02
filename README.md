# KIM Chatbot

This is the repository for the KIM Chatbot, an LLM-driven asisstant for the reflection of study subjects. It was developed in the <PROJECT?> in cooperation with the IAAI at HdM from 2024-2025.

<p align="center">
  <img src="doc/img/kim.png" alt="grafik" width="420"/>
</p>

## Key Features
* Interaction for reflective discussion in natural language.
* New models or new/adjusted sysprompts can be configured.
* Easy setup within docker.


## Installation & Setup

The KIM-Chatbot can be run either by using the (1) image from dockerhub, (2) building the docker image locally from scratch or (3) running the application straight via Python.

### (1) Using the docker image from dockerhub (recommended)

1. If you haven't already, install [Docker](https://docs.docker.com/desktop/).
2. Pull the image from dockerhub: ``docker pull frupp/llm-chatbot`` .
3. Create a directory where chats should be saved.
4. Run and create a container: ``docker run -d -p 8501:8501 --name llm-chatbot -v <path-to-save-dir>:/llm-chatbot/data frupp/llm-chatbot`` .
5. The KIM Chatbot will then be available at localhost:8501 .

### (2) Building the docker image locally

1. If you haven't already, install [Docker](https://docs.docker.com/desktop/).
2. Navigate to the ``code/`` directory and run: ``docker build -t llm-chatbot:latest`` .
3. Create a directory where chats should be saved.
4. Run and create a container: ``docker run -d -p 8501:8501 --name llm-chatbot -v <path-to-save-dir>:/llm-chatbot/data llm-chatbot`` .
5. The KIM Chatbot will then be available at localhost:8501 .

### (3) Running the application with Python directly

1. Install Python $\ge$ 3.11 .#
2. Navigate to ``code/`` .
3. Install additionally required modules via: ``pip install -r requirements.txt`` .
4. Create the following environment variables:
```
ENV CHAT_PATH=data/chat
ENV ENDPOINTS_CONFIG=data/endpoints.json 
ENV MODELS_CONFIG=data/models.json
ENV GUI_CONFIG=data/gui_config.json
ENV DATABASE_PATH=data/chatbot.db
ENV TIME_LIMIT_DELTA_SECONDS=60
ENV RATE_LIMIT_FRACTION_LEFT=0.3
```
5. Run ``streamlit run main.py``

## Code
The code can be found in ``code/``. We will soon provide a more detailed documentation of the code and its modules here.
