import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"
TIMEOUT_SECONDS = 10


class Translator:

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return text

        prompt = (
            "You are a translation engine.\n"
            "Translate the input to English only.\n"
            "Do not explain.\n"
            "Do not add commentary.\n"
            "Output only the translated sentence.\n\n"
            f"Input:\n{text}\n\nOutput:"
        )

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0
            }
        }

        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=TIMEOUT_SECONDS
            )
        except Exception as e:
            raise RuntimeError(f"Translator connection failed: {e}")

        if response.status_code != 200:
            raise RuntimeError(
                f"Translator HTTP error {response.status_code}: {response.text}"
            )

        data = response.json()

        translated = data.get("response", "").strip()

        if not translated:
            raise RuntimeError("Translator returned empty response")

        # Safety guard: prevent accidental long hallucinated output
        if len(translated.split()) > 50:
            raise RuntimeError("Translator output suspiciously long")

        return translated
