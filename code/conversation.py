from openai import APIConnectionError, APITimeoutError, InternalServerError
from httpx import RemoteProtocolError
import streamlit as st
from datetime import datetime
from config import create_chat_generator, create_summary_generator

class Conversation:
    def __init__(self, name, course, agree_terms, survey_code, role) -> None:
        self.name = name
        self.course = course
        self.agree_terms = agree_terms
        self.survey_code = survey_code
        self.role = role
        self.messages = []
        self.model = None
        self.summary_model = None
        self.state = "new" # new, running, end
        self.happiness = []
        self.start_time = None
        self.end_time = None
        self._user_messages = []
        self._current_generator = None
        self._update_summary = False
        self.summary = ""

    def add_user_message(self, message: str):
        self._user_messages.append({"role": "user", "content": message, "timestamp": datetime.now().isoformat()})

    def handle_messages(self):
        self.display_old_messages()

        while self._user_messages:
            self._update_summary = True
            user_message = self._user_messages[0]
            if self._current_generator is None:
                self.messages.append(user_message)
                self._current_generator = self._collect_response_tokens()
                with st.chat_message("user"):
                    st.markdown(user_message["content"])

            if self._current_generator is not None:
                self._current_generator = self._collect_response_tokens()
                self._display_current_response()
            _ = self._user_messages.pop(0)

    def _collect_response_tokens(self):
        for chunk in create_chat_generator(self.messages, self.model):
            yield chunk

        self._current_generator = None


    def _display_current_response(self):
        try:
            with st.chat_message("assistant", avatar="🧑‍💻"):
                content = st.write_stream(self._current_generator)

            self.messages.append({"role": "assistant", "content": content, "timestamp": datetime.now().isoformat()})
            self.current_response = []

        except RemoteProtocolError:
            st.info("Achtung Chatbot Limit erreicht! Es kann nicht weiter gechattet werden! Bitte speichern!")
        except (APITimeoutError, APIConnectionError, InternalServerError) as e:
            st.error(f"Chatbot currently not available! {e}")
            print(e)

    def display_old_messages(self):
        for message in st.session_state.conversation.messages:
            if message["role"] == "system":
                continue
            if message["role"] == "assistant":
                avatar="🧑‍💻"
            else:
                avatar=None
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    def add_happiness_entry(self, happy):
        if happy:
            self.happiness.append({"state": "happy", "timestamp": datetime.now().isoformat()})
        else:
            self.happiness.append({"state": "not happy", "timestamp": datetime.now().isoformat()})

    def reset(self):
        self.messages = []
        self.model = None
        self.state = "end"
        st.session_state["model_select"] = None
        st.rerun()

    def get_summary(self):
        if self._update_summary:
            self._summary = "".join(create_summary_generator(self.messages, self.model))
            self._update_summary = False
        return self._summary
