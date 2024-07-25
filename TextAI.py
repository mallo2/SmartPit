from dotenv import get_key
from groq import Groq


def send_request(groq, audio_text) -> str:
    chat_completion = groq.chat.completions.create(
        messages=[
            {"role": "system", "content": get_key('.env', 'PROMPT_REQUEST')},
            {"role": "user", "content": audio_text}
        ],
        model=get_key('.env', 'GROQ_MODEL')
    )
    return chat_completion.choices[0].message.content


class TextAI:
    def __init__(self):
        self.model = Groq(api_key=get_key('.env', 'GROQ_API_KEY'))

    def process_request(self, audioAI) -> str:
        audio_text = audioAI.transcribe_audio()
        return send_request(self.model, audio_text=audio_text)
