import json
from datetime import datetime

import config

def save_aborted(conversation, reason=None, anonymize_name=True, anonymize_full=False):
    return _save(conversation, anonymize_name=anonymize_name, anonymize_full=anonymize_full, reason=reason)


def save_all(conversation, anonymize_name=True, anonymize_full=False):
    return _save(conversation, anonymize_name=anonymize_name, anonymize_full=anonymize_full)


def _save(conversation, anonymize_name=False, anonymize_full=False, reason=None):
    session_dict = _get_session_dict(conversation)
    if reason is not None:
        session_dict["abort_reason"] = reason
    _append_messages(session_dict, conversation)
    session_summary = _get_session_summary(session_dict, conversation)
    session_dict["summary"] = session_summary

    if anonymize_name or anonymize_full:
        _anonymize_name(session_dict)

    if anonymize_full:
        _anonymize_full(session_dict["messages"])

    file_path = f'{config.CHAT_PATH}/{session_dict["session_name"]}.json'
    file_path = file_path.replace(":", "-")

    with open(file_path, 'w', encoding="utf8") as f:
        json.dump(session_dict, f, indent=4, ensure_ascii=False)

    return session_summary


def _append_messages(session_dict, conversation):
    new_messages = _format_messages(conversation.messages)
    session_dict["messages"] = new_messages
    session_dict["messages"] = [_get_msg_meta_data(m) for m in session_dict["messages"]]


def _format_messages(messages):
    return [{**m, "annotation": "", "rating": 0, "timestamp": m["timestamp"]} for m in messages]


def _get_session_dict(conversation):
    session_name = f'{conversation.name}-{conversation.model}-{conversation.start_time}'

    return {
        "session_name": session_name,
        "course": conversation.course,
        "user": conversation.name,
        "survey_code": conversation.survey_code,
        "model": str(conversation.model),
        "system_prompt": conversation.model.system_prompt,
        "start_time": conversation.start_time,
        "end_time": conversation.end_time,
        "messages": [],
        "happiness": conversation.happiness
    }


def _anonymize_name(session_dict):
    name = session_dict["user"]
    session_dict["user"] = "ANONYMIZED"
    session_dict["session_name"] = session_dict["session_name"].replace(name, session_dict["user"])
    for m in session_dict["messages"]:
        m["content"] = m["content"].replace(name, session_dict["user"])


def _anonymize_full(messages):
    for m in messages:
        m["content"] = "ANONYMIZED"


def _get_msg_meta_data(message):
    message["number_tokens"] = len(message["content"].split(" "))
    message["number_characters"] = len(message["content"])
    return message


def _get_session_summary(session_dict, conversation):
    summary = {}
    summary["user_number_messages"] = len([m for m in session_dict["messages"] if m["role"] == "user"])
    summary["assistant_number_messages"] = len([m for m in session_dict["messages"] if m["role"] == "assistant"])
    summary["user_number_messages_with_?"] = len([m for m in session_dict["messages"] if m["role"] == "user" and "?" in m["content"]])
    summary["assistant_number_messages_with_?"] = len([m for m in session_dict["messages"] if m["role"] == "assistant" and "?" in m["content"]])

    summary["user_total_number_tokens"] = sum([m["number_tokens"] for m in session_dict["messages"] if m["role"] == "user"])
    summary["assistant_total_number_tokens"] = sum([m["number_tokens"] for m in session_dict["messages"] if m["role"] == "assistant"])
    summary["user_total_number_characters"] = sum([m["number_characters"] for m in session_dict["messages"] if m["role"] == "user"])
    summary["assistant_total_number_characters"] = sum([m["number_characters"] for m in session_dict["messages"] if m["role"] == "assistant"])

    start = datetime.strptime(conversation.start_time, "%Y-%m-%dT%H:%M:%S.%f")
    end = datetime.strptime(conversation.end_time, "%Y-%m-%dT%H:%M:%S.%f")
    summary["total_chat_duration"] = (end - start).total_seconds()
    summary["total_chat_duration_time_format"] = "seconds"
    return summary
