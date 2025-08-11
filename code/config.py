import os
from pathlib import Path
import streamlit as st
from endpoints import get_endpoints
from models import Model, get_models
import sqlite3
from datetime import datetime, timedelta
import json

CHAT_PATH = None
GUI_CONFIG = {}

def init_config():
    global CHAT_PATH
    CHAT_PATH = os.environ.get("CHAT_PATH", "chat")
    Path(CHAT_PATH).mkdir(parents=True, exist_ok=True)

    if "endpoints" not in st.session_state:
        endpoints_config_path = os.environ.get("ENDPOINTS_CONFIG", 'endpoints.json')
        models_config_path = os.environ.get("MODELS_CONFIG", 'models.json')
        endpoints = get_endpoints(endpoints_config_path)
        if endpoints:
            st.session_state["endpoints"] = endpoints
            st.session_state["models"] = get_models(models_config_path, st.session_state["endpoints"])
        else:
            st.error("No endpoints found! Please configure one in endpoints.json")

    GUI_CONFIG_FILE = os.environ.get("GUI_CONFIG", "gui_config.json")
    with open(GUI_CONFIG_FILE, mode="r", encoding="utf-8") as f:
        GUI_CONFIG.update(json.load(f))

    init_database()

def create_chat_generator(messages, model: Model):
    new_messages = [{"role": message["role"], "content": message["content"]} for message in messages]
    endpoint = st.session_state["endpoints"][model.endpoint_name]
    return endpoint.chat(new_messages, model.model, model.temperature, model.top_p)
    

def create_summary_generator(messages, model: Model):
    new_messages = [{"role": "system", "content": model.summary_prompt}]

    # always use user role
    new_messages.extend({"role": "user", "content": message["content"]} for message in messages[1:])
    endpoint = st.session_state["endpoints"][model.endpoint_name]
    return endpoint.chat(new_messages, model.model, model.temperature, model.top_p)


def init_database():
    try:
        with sqlite3.connect(os.environ.get("DATABASE_PATH", 'chatbot.db')) as conn:
            conn.execute('PRAGMA journal_mode=WAL;')
            cursor = conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limit (
                id INTEGER PRIMARY KEY,
                current_rate INTEGER,
                rate_limit INTEGER,
                date_stored TEXT
            )
            ''')

            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_date_stored
            ON rate_limit (date_stored)
            ''')

            # avoiding an empty table and therefor denying all new chats
            cursor.execute('SELECT COUNT(*) FROM rate_limit')
            count = cursor.fetchone()[0]
            if count == 0:
                insert_rate_limit(1000, 1000)

            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"sqlite error: {e}")

def insert_rate_limit(current_rate: int, rate_limit: int):
    try:
        with sqlite3.connect(os.environ.get("DATABASE_PATH", 'chatbot.db')) as conn:
            cursor = conn.cursor()

            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
            INSERT INTO rate_limit (current_rate, rate_limit, date_stored)
            VALUES (?, ?, ?)
            ''', (current_rate, rate_limit, current_date))

            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"sqlite error: {e}")

def enough_rate_limit_left():
    try:
        with sqlite3.connect(os.environ.get("DATABASE_PATH", 'chatbot.db')) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT current_rate, rate_limit, date_stored FROM rate_limit
            ORDER BY date_stored DESC
            LIMIT 1
            ''')
            latest_row = cursor.fetchone()

            if latest_row:
                current_rate, rate_limit, date_stored = latest_row
                stored_time = datetime.strptime(date_stored, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.now()

                # Check if the difference is greater than one minute
                if current_time - stored_time > timedelta(seconds=float(os.environ.get("TIME_LIMIT_DELTA_SECONDS", 60))):
                    return True
                else:
                    return current_rate / rate_limit > float(os.environ.get("RATE_LIMIT_FRACTION_LEFT", 0.3))
            else:
                return False
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return False
