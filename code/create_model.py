import streamlit as st
from models import Model, save_models

def is_valid(base_model, model_name):
    if not base_model:
        st.error("Please choose a base model")

    if not model_name:
        st.error("Please insert a model name")


def remove_default_from_models(keep:Model):
    for model in st.session_state["models"]:
        if model != keep:
            model.default = False


model: Model|None = None
if st.session_state["models"]:
    model = st.selectbox(
        "Models",
        st.session_state["models"],
        index = None,
        placeholder="copy or modify a existing model"
    )

index = None
if model:
    index = list(st.session_state["endpoints"].keys()).index(model.endpoint_name)
endpoint = st.selectbox(
    "Endpoints",
    st.session_state["endpoints"].keys(),
    index = index
)

if endpoint:
    endpoint = st.session_state["endpoints"][endpoint]

    system_prompt_message = ""
    if model:
        system_prompt_message = model.system_prompt
    system_prompt = st.text_area(label="System prompt", height=500, value=system_prompt_message)

    summary_prompt_message = ""
    if model:
        summary_prompt_message = model.summary_prompt
    summary_prompt = st.text_area(label="Summary prompt", height=500, value=summary_prompt_message)

    model_list = endpoint.model_list()

    index = None
    if model:
        try:
            index = model_list.index(model.model)
        except ValueError:
            index = None
            st.info(f"Model {model.model} not available")
    base_model = st.selectbox(
        "base model:",
        model_list,
        index=index
    )


    value = None
    if model:
        value = model.temperature
    temperature = None
    if st.checkbox("Temperature", value=value is not None):
        temperature = st.number_input("Temperature", value=value)

    value = None
    if model:
        value = model.top_p
    top_p = None
    if st.checkbox("top p", value is not None):
        top_p = st.number_input("top_p", value=value)

    name = None
    if model:
        name = model.name
    model_name = st.text_input(label="model name", value=name)

    default = None
    if model:
        default = model.default
    default_model = st.checkbox("use this model as default", value=default)

    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        if st.button("create model"):
            is_valid(base_model, model_name)

            if base_model and model_name:
                new_model = Model(endpoint.name, model_name, base_model, system_prompt, summary_prompt, temperature=temperature, top_p=top_p, default=default_model)
                if new_model in st.session_state["models"]:
                    st.error(f"Model {new_model.name} already exists")
                else:
                    st.session_state["models"].append(new_model)
                    remove_default_from_models(new_model)
                    save_models(st.session_state["models"])
                    st.success("Model created")
    with col2:
        if st.button("update model", disabled=model is None):
            is_valid(base_model, model_name)
            if model and base_model and model_name:
                model.endpoint_name = endpoint.name
                model.name = model_name
                model.model = base_model
                model.system_prompt = system_prompt
                model.summary_prompt = summary_prompt
                model.temperature = temperature
                model.top_p = top_p
                model.default = default_model
                remove_default_from_models(model)
                index = st.session_state["models"].index(model)
                st.session_state["models"][index] = model
                save_models(st.session_state["models"])
                st.success("Model updated")
    with col3:
        if st.button("delete model", disabled=model is None):
            st.session_state["models"].remove(model)
            save_models(st.session_state["models"])
            st.rerun()
