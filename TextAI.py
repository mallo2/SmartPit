import logging

from dotenv import get_key
from groq import Groq


class TextAI:
    """
    FR : Classe permettant de gérer l'IA de texte\n
    EN : Class to manage the text AI
    """

    def __init__(self):
        """
        FR : Constructeur de la classe TextAI\n
        EN : Constructor of the TextAI class
        """
        self.__model = Groq(api_key=get_key('.env', 'GROQ_API_KEY'))
        logging.info("TextAI initialized")

    def process_request(self, request: str) -> dict:
        """
        FR : Méthode permettant de traiter la demande avec un appel à l'API de Groq\n
        EN : Method to process the request with a call to the Groq API
        :param request: (str)
            FR : Demande de l'utilisateur
            EN : User request
        :return: (dict)
            FR : Réponse de l'IA
            EN : AI response
        """
        chat_completion = self.__model.chat.completions.create(
            messages=[
                {"role": "system", "content": get_key('.env', 'PROMPT_REQUEST')},
                {"role": "user", "content": request}
            ],
            model=get_key('.env', 'GROQ_MODEL_REQUEST'),
            temperature=0.2
        )
        response = chat_completion.choices[0].message.content
        return {
            "audio_text": request,
            "response": response
        }

    def generate_response(self, question: str, data: str) -> str:
        """
        FR : Méthode permettant de générer une réponse avec un appel à l'API de Groq\n
        EN : Method to generate a response with a call to the Groq API
        :param question: (str)
            FR : Question de l'utilisateur
            EN : User question
        :param data: (str)
            FR : Données de course\n
            EN : Race data
        :return: (str)
            FR : Réponse de l'IA
            EN : AI response
        """
        chat_completion = self.__model.chat.completions.create(
            messages=[
                {"role": "system", "content": get_key('.env', 'PROMPT_RESPONSE')},
                {"role": "user", "content": f"Question : {question}. Données de course : {data}"}
            ],
            model=get_key('.env', 'GROQ_MODEL_RESPONSE'),
            temperature=0.5
        )
        return chat_completion.choices[0].message.content
