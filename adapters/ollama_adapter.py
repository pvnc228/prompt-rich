import requests
class OllamaAdapter:
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.generate_url = f"{base_url}/api/generate"
        self._check_model_available()
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7):
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        response=self._make_request(payload)
        return response["response"].strip()
    def _make_request(self, payload: dict) -> dict:
        response=requests.post(self.generate_url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise Exception(f"Model {self.model_name} not found")
        else:
            raise Exception(f"Ollama request failed: {response.text}")
    def _check_model_available(self) -> None:
        response=requests.get(f"{self.base_url}/api/tags")
        if response.status_code != 200:
            raise Exception
        models = response.json().get("models", [])
        model_names = [model["name"] for model in models]
        if self.model_name not in model_names:
            base_name=self.model_name.split(":")[0]
            found = any(base_name in name for name in model_names)
            if not found:
                raise Exception(f"Model {self.model_name} not found. Run: ollama pull {self.model_name}")
