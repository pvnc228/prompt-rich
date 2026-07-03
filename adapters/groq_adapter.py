from time import sleep
import requests
class GroqAdapter:
    def __init__(self, api_key: str, model_name: str = "openai/gpt-oss-120b"):
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
    def generate(self, prompt: str, max_tokens: int = 4096, temperature: float = 0.7) -> str:
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = self._make_requests(payload)
        self._handle_errors(response)
        return response.get("choices", [{}])[0].get("message", {}).get("content", "")
    def _make_requests(self, payload: dict) -> dict:
        response=requests.post(self.base_url, headers=self.headers, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            sleep(5)  
            return self._make_requests(payload)  
        elif 400 <= response.status_code < 500:
            self._handle_errors(response.json())
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
    def _handle_errors(self, response: dict):
        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            raise Exception(f"Groq API error: {error_msg}")
        elif not(response.get("choices")):
            raise Exception("No choices in Groq response")

