FROM python:3.11-slim
LABEL authors="Florian Rupp, Tobias Malmsheimer"

WORKDIR /llm-chatbot
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV CHAT_PATH=data/chat
# copy endpoints.json manually to avoid apikeys in git
ENV ENDPOINTS_CONFIG=data/endpoints.json 
ENV MODELS_CONFIG=data/models.json
ENV GUI_CONFIG=data/gui_config.json
ENV DATABASE_PATH=data/chatbot.db
ENV TIME_LIMIT_DELTA_SECONDS=60
ENV RATE_LIMIT_FRACTION_LEFT=0.3

ENTRYPOINT ["streamlit", "run", "main.py"]
EXPOSE 8501
