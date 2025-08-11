from datetime import datetime
import streamlit as st
from data import save_aborted, save_all
from config import GUI_CONFIG


save_info = "Die Projektbeteiligten würden für eine weitere Auswertung im Rahmen der projektbezogenen Forschung gerne auf die Inhalte des Gesprächs zugreifen. Dein Name wird jedoch immer anonymisiert. Stimmst Du zu, dass der ansonsten vollständige Verlauf des Gesprächs zu diesem Zweck gespeichert wird? "


def send_to_soscisurvey():
    if st.session_state.conversation.survey_code is not None and "session_summary" in st.session_state:
        summary_fields = ""
        for key, value in st.session_state.session_summary.items():
          summary_fields += f'<input type="hidden" name="{key}" value="{value}">\n'

        st.html(f"""
        <form id="soscisurvey" action="https://www.soscisurvey.de/KIM-Test_nach/" method="POST">
          <input type="hidden" name="code" value="{st.session_state.conversation.survey_code}">
          {summary_fields}
          <input type="submit" value="Weiter zur Umfrage"/>
        </form>
        """)


@st.dialog("Warum hast Du abgebrochen?")
def abort_dialog():
    st.session_state.conversation.end_time = datetime.now().isoformat()
    reason = st.text_area(label="Grund")
    st.header("Soll der Chatverlauf gespeichert werden?")
    st.text(save_info)
    if st.button("Ja", icon="✅", use_container_width=True):
        st.session_state.session_summary = save_aborted(st.session_state.conversation, reason=reason, anonymize_name=True, anonymize_full=False)
        st.session_state.conversation.reset()

    if st.button("Nein", icon="❌", use_container_width=True):
        st.session_state.session_summary = save_aborted(st.session_state.conversation, reason=reason, anonymize_name=True, anonymize_full=True)
        st.session_state.conversation.reset()


@st.dialog("Admin Token eingeben um Konfigurationsmodus zu aktivieren")
def admin_dialog():
    token = st.text_input("Admin Token", type="password")
    if st.button("Senden"):
        if token == GUI_CONFIG["admin_token"]:
            st.session_state["role"] = "admin"
            st.rerun()
        else:
            st.error("Ungültiger Admin Token")


@st.dialog("Soll der Chatverlauf gespeichert werden?")
def finish_dialog():
    st.session_state.conversation.end_time = datetime.now().isoformat()
    st.text(save_info)
    if st.button("Ja", icon="✅", use_container_width=True):
        st.session_state.session_summary = save_all(st.session_state.conversation, anonymize_name=True, anonymize_full=False)
        st.session_state.conversation.reset()

    if st.button("Nein", icon="❌", use_container_width=True):
        st.session_state.session_summary = save_all(st.session_state.conversation, anonymize_name=True, anonymize_full=True)
        st.session_state.conversation.reset()


def change_model():
    st.session_state.conversation.messages = []
    st.session_state.conversation.state = "new"
    st.session_state["timestamp"] = datetime.now().isoformat()
    if st.session_state["model_select"] is not None:
        st.session_state.conversation.model = st.session_state["model_select"]
        st.session_state.conversation.messages = [st.session_state["model_select"].create_system_message()]
        st.session_state.conversation.add_user_message(f"Hallo ich bin {st.session_state.conversation.name} und habe in diesem Semester in den Schlüsselkompetenzen die Veranstaltung {st.session_state.conversation.course} besucht.")

    st.session_state.new_chat = True
    st.session_state.conversation.start_time = datetime.now().isoformat()

if st.session_state.conversation.state == "end":
    st.markdown(
        "<h5 style='text-align: center;'>Vielen Dank für die Teilnahme.</h5>",
        unsafe_allow_html=True)
    send_to_soscisurvey()

else:
    if st.session_state["role"] == "admin":
        model = st.selectbox(
            label="Model:",
            options=st.session_state["models"],
            on_change=change_model,
            placeholder="choose a model",
            key="model_select",
            index=None
        )
    else:
        models = st.session_state["models"]
        if not models:
            st.error("No models found! Please create one in config mode.")
            model = None
        else:
            default_model = list(filter(lambda model: model.default, models))
            if len(default_model) == 0:
                st.error("No default model set! Please configure one in config mode.")
                model = None
            else:
                model = default_model[0]
            if "new_chat" not in st.session_state:
                st.session_state["model_select"] = model
                change_model()
    st.session_state.conversation.model = model

    if model:
        user_input = st.chat_input("Schreibe hier deine Nachricht...")
        if st.session_state.conversation.state == "new":
            st.session_state.conversation.start_time = datetime.now().isoformat()
            st.session_state.conversation.handle_messages()
            st.session_state.conversation.state = "running"
        else:
            if user_input:
                st.session_state.conversation.add_user_message(user_input)
                st.session_state.conversation.handle_messages()
                st.session_state.conversation.end_time = datetime.now().isoformat()
                st.session_state.session_summary = save_all(st.session_state.conversation, anonymize_name=True, anonymize_full=True)
            else:
                st.session_state.conversation.display_old_messages()

    with st.container():
        if "happiness_buttons_visible" in GUI_CONFIG and GUI_CONFIG["happiness_buttons_visible"]:
            with st.container():
                st.subheader(
                    "Wie fühlt sich dieser Moment gerade für dich an?",
                    help="""
- ➕ → wenn du etwas als angenehm, positiv fühlst

- ➖ → wenn du etwas als unangenehm, negativ fühlst

Diese Markierungen helfen uns zu verstehen, wie sich die Nutzung anfühlt – es geht also um dein Erleben, nicht um richtige Antworten.

Du kannst es dir wie ein Gefühlsthermometer vorstellen. Auch kleine Veränderungen sind von Bedeutung. Wenn du unsicher bist ob es ein bisschen positiv oder negativ ist, einfach drücken.
                    """)
                col1, col2 = st.columns([1,1])
                with col1:
                    if good := st.button("", icon="➕", use_container_width=True):
                        st.session_state.conversation.add_happiness_entry(True)

                with col2:
                    if bad := st.button("", icon="➖", use_container_width=True):
                        st.session_state.conversation.add_happiness_entry(False)


    with st.sidebar:
        if "summary_visible" in GUI_CONFIG and GUI_CONFIG["summary_visible"] or st.session_state.role == "admin" and model:
            st.header("Zusammenfassung")
            st.markdown(st.session_state.conversation.get_summary())

        if "save_buttons_visible" in GUI_CONFIG and GUI_CONFIG["save_buttons_visible"]:
            with st.container():
                st.subheader("Gespräch beenden")
                if st.button("Danke für das Gespräch. Bis zum nächsten Mal.", use_container_width=True):

                    finish_dialog()
                if st.button("Gespräch vorzeitig abbrechen.", use_container_width=True):
                    abort_dialog()

        if st.session_state["role"] != "admin":
            if st.button("Config-Mode"):
                admin_dialog()

