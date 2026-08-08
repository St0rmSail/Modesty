"""Small client for Ollama's local chat endpoint."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "gemma4:e2b"


class OllamaChatClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def chat(self, messages: list[dict[str, str]]) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "stream": False,
            }
        ).encode("utf-8")

        request = Request(
            OLLAMA_CHAT_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=300) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            if error.code == 404:
                raise RuntimeError(
                    f"The Ollama model '{self.model}' is not available."
                ) from error
            raise RuntimeError(f"Ollama returned an error: {detail}") from error
        except URLError as error:
            raise RuntimeError(
                "Ollama is not responding. Start Ollama and try again."
            ) from error
        except TimeoutError as error:
            raise RuntimeError(
                "The local model took too long to answer. It may still be loading."
            ) from error
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise RuntimeError("Ollama returned an unreadable response.") from error

        content = result.get("message", {}).get("content", "").strip()
        if not content:
            raise RuntimeError("Ollama returned an empty response.")

        return content
