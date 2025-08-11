import json
import os
from datetime import datetime


class Model:
    def __init__(self, endpoint_name: str, name: str, model: str, system_prompt: str, summary_prompt:str = None, temperature:float=None, top_p:float=None, default=False) -> None:
        self.name = name
        self.endpoint_name = endpoint_name
        self.model = model
        self.system_prompt = system_prompt
        self.summary_prompt = summary_prompt
        self.temperature = temperature
        self.top_p = top_p
        self.default = default

    def to_dict(self):
        return {
            "endpoint_name": self.endpoint_name,
            "name": self.name,
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "system_prompt": self.system_prompt,
            "summary_prompt": self.summary_prompt,
            "default": self.default
        }

    def create_system_message(self):
        return {"role": "system", "content": self.system_prompt, "timestamp": datetime.now().isoformat()}

    def __str__(self) -> str:
        return f"{self.name} - {self.endpoint_name}"

    def __eq__(self, value: object, /) -> bool:
        if value is None:
            return False
        return self.name == value.name


def get_models(path, endpoints) -> list[Model]:
    if not os.path.exists(path):
        return []
    with open(path, mode="r", encoding="utf-8") as f:
        model_json = json.load(f)

        models = []
        for model in model_json:
            if model["endpoint_name"] not in endpoints:
                print(f"Warning: Unkown endpoint {model['endpoint_name']}")
            else:
                models.append(
                    Model(
                        model["endpoint_name"],
                        model["name"],
                        model["model"],
                        model["system_prompt"],
                        model["summary_prompt"] if "summary_prompt" in model else "",
                        temperature=model["temperature"],
                        top_p=model["top_p"],
                        default=model["default"]
                    )
                )
        return models


def save_models(models: list[Model]):
    models_config_path = os.environ.get("MODELS_CONFIG", 'models.json')
    with open(models_config_path, mode="w", encoding="utf-8") as f:
        json.dump([model.to_dict() for model in models], f, indent=2)
