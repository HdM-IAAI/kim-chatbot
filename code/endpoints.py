from abc import ABC, abstractmethod
from typing import Iterator
from openai import OpenAI
import json
import ollama
import config
import os


class Endpoint(ABC):
    def __init__(self, endpoint: ollama.Client|OpenAI, name: str) -> None:
        self._endpoint:ollama.Client|OpenAI = endpoint
        self.name = name

    @abstractmethod
    def chat(self, messages, model:str, temperature:float, top_p:float) -> Iterator:
        ...

    @abstractmethod
    def model_list(self) -> list:
        ...

class OllamaEndpoint(Endpoint):
    def chat(self, messages, model:str, temperature:float, top_p:float) -> Iterator:
        for chunk in self._endpoint.chat(
                messages=messages,
                model=model,
                options={"temperature": temperature, "top_p": top_p},
                stream=True):
            yield chunk["message"]["content"]

    def model_list(self) -> list:
        return [model["model"] for model in self._endpoint.list()["models"]]


class OpenAIEndpoint(Endpoint):
    def chat(self, messages, model:str, temperature:float, top_p:float) -> Iterator:
        response = self._endpoint.chat.completions.with_raw_response.create(
                messages=messages,
                model=model,
                temperature=temperature,
                top_p=top_p,
                stream=True)

        current_rate = int(response.headers["x-ratelimit-remaining-hour"])
        rate_limit = int(response.headers["x-ratelimit-limit-hour"])
        config.insert_rate_limit(current_rate, rate_limit)

        for chunk in response.parse():
            yield "".join(choice.delta.content for choice in chunk.choices)

    def model_list(self) -> list:
        return [model.id for model in self._endpoint.models.list().data]


def get_endpoints(path):
    if not os.path.exists(path):
        return []

    with open(path, mode="r", encoding="utf-8") as f:
        client_json = json.load(f)

        clients = {}

        for entry in client_json:
            if entry["type"] == "ollama":
                clients[entry["name"]] = OllamaEndpoint(
                    endpoint=ollama.Client(host=entry["endpoint"]),
                    name=entry["name"])
            elif entry["type"] == "openai":
                clients[entry["name"]] = OpenAIEndpoint(
                    endpoint=OpenAI(base_url=entry["endpoint"], api_key=entry["api_key"]),
                    name=entry["name"])
            else:
                print("unsupported endpoint")

        return clients
