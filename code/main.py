import streamlit as st
import config
from conversation import Conversation

config.init_config()

if "endpoints" in st.session_state:
    if "conversation" not in st.session_state and not config.enough_rate_limit_left():
        st.error("Sorry, zur Zeit viel los :(")
    else:
        if "role" not in st.session_state:
            st.session_state["role"] = "student"

        if st.session_state["role"] == "admin" and "permission" in st.session_state:
            pg = st.navigation([
                st.Page("chatbot.py", title="Chatting", icon="🤖"),
                st.Page("create_model.py", title="Create and modify models", icon="⚙️"),
            ])

            st.markdown("<h1 style='text-align: center;'>Kim</h1>", unsafe_allow_html=True)
            st.markdown(
                "<h5 style='text-align: center;'>Deine Unterstützung bei der Reflexion der Schlüsselkompetenz-Veranstaltungen </h5>",
                unsafe_allow_html=True)
            pg.run()

        if st.session_state["role"] == "student" and "permission" in st.session_state:
            pg = st.navigation([
                st.Page("chatbot.py", title="Chatting", icon="🤖"),
            ])

            st.markdown("<h1 style='text-align: center;'>Kim</h1>", unsafe_allow_html=True)
            st.markdown(
                "<h5 style='text-align: center;'>Deine Unterstützung bei der Reflexion der Schlüsselkompetenz-Veranstaltungen </h5>",
                unsafe_allow_html=True)

            pg.run()

        if "permission" not in st.session_state and "role" in st.session_state:
            st.markdown("<h1 style='text-align: center;'>Willkommen bei Kim</h1>", unsafe_allow_html=True)
            st.markdown(
                "<h5 style='text-align: center;'>Deine Unterstützung bei der Reflexion der Schlüsselkompetenz-Veranstaltungen </h5>",
                unsafe_allow_html=True)

            left_space, center, right_space = st.columns([1, 2, 1])
            with center:
                input_name = st.text_input("Wie heißt du?", key="name")
                input_course = st.text_input("Über welche Veranstaltung aus den Schlüsselkompetenzen möchtest du reflektieren?", key="course")

            st.markdown(
                """
                <div style="border: 1px solid #ccc; padding: 10px; height: 280px; overflow-y: scroll;">
    Diese Webanwendung wird auf einem Server der HdM betrieben. Die für die Chatfunktion erforderlichen Sprachmodelle werden in einem Rechenzentrum der Gesellschaft für wissenschaftliche Datenverarbeitung mbH Göttingen (GWDG) betrieben. Auf dem HdM-Server werden nur die folgenden Daten gespeichert: Zeitpunkt und Dauer des Gesprächs, die angegebene Veranstaltung sowie Anzahl und Länge der Interaktionen im Gesprächsverlauf. Der eingegebene Name und die Inhalte des Gesprächs werden zu keinem Zeitpunkt auf Datenträgern gespeichert.
    Auf den Servern der GWDG werden nur der Zeitpunkt und die Länge aller Anfragen und Antworten sowie das von uns zum Zugang zu den Diensten verwendete Nutzerkonto protokolliert. Die Inhalte der Interaktionen werden nicht gespeichert. Details findest Du unter <a href="https://datenschutz.gwdg.de/services/chatai">https://datenschutz.gwdg.de/services/chatai</a> (Rubrik "Allgemeine Nutzung von Modellen)." 
                </div>
                """,
                unsafe_allow_html=True,
            )

            left_space, center, right_space = st.columns([1, 2, 1])
            with (center):
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)  # small padding here
                agree_terms = st.checkbox("Ja, ich stimme den obigen Bedingungen zu.")
                st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)  # small padding here

                # Confirmation message
                if input_name and input_course and agree_terms:
                    st.success("Danke, dann kann es los gehen!")
                    if "code" in st.query_params:
                        survey_code = st.query_params["code"]
                    else:
                        survey_code = None
                    st.session_state["conversation"] = Conversation(input_name, input_course, agree_terms, survey_code, st.session_state.role)
                    button_disabled = False
                else:

                    st.info(
                        "Bitte gib deinen Namen und Kurs ein, sowie stimme den Bedingungen zu.")
                    button_disabled = True

                if button_disabled is True:
                    st.button("Start", disabled=True, use_container_width=True)
                else:
                    def allow_permission():
                        st.session_state["permission"] = True
                    st.button("Start", use_container_width=True, on_click=allow_permission)
