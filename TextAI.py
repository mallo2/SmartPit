from dotenv import get_key
from groq import Groq


class TextAI:
    def __init__(self):
        """
        FR : Constructeur de la classe TextAI\n
        EN : Constructor of the TextAI class
        """
        self.model = Groq(api_key=get_key('.env', 'GROQ_API_KEY'))

    def process_request(self, audioAI) -> dict:
        """
        FR : Méthode permettant de traiter la demande avec un appel à l'API de Groq\n
        EN : Method to process the request with a call to the Groq API
        :param audioAI:
        :return:
        """
        audio_text = audioAI.transcribe_audio()
        chat_completion = self.model.chat.completions.create(
            messages=[
                {"role": "system", "content": get_key('.env', 'PROMPT_REQUEST')},
                {"role": "user", "content": audio_text}
            ],
            model=get_key('.env', 'GROQ_MODEL'),
            temperature=0.2
        )
        response = chat_completion.choices[0].message.content
        return {
            "audio_text": audio_text,
            "response": response
        }

    def generate_response(self, question, data) -> str:
        """
        FR : Méthode permettant de générer une réponse avec un appel à l'API de Groq\n
        EN : Method to generate a response with a call to the Groq API
        :param question:
        :param data:
        :return:
        """
        chat_completion = self.model.chat.completions.create(
            messages=[
                {"role": "system", "content": get_key('.env', 'PROMPT_RESPONSE')},
                {"role": "user", "content": f"Question : {question}. Données de course : {data}"}
            ],
            model=get_key('.env', 'GROQ_MODEL'),
            temperature=0.5
        )
        return chat_completion.choices[0].message.content
