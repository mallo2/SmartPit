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
        self.__groq_api_key = get_key('.env', 'GROQ_API_KEY')
        self.__groq_model = get_key('.env', 'GROQ_MODEL')
        self.__prompt_request = get_key('.env', 'PROMPT_REQUEST')
        self.__prompt_response = get_key('.env', 'PROMPT_RESPONSE')
        self.__groq = Groq(api_key=self.__groq_api_key)
        logging.info("TextAI initialized")

    def update_groq_api_key(self) -> None:
        """
        FR : Méthode permettant de mettre à jour la clé API de Groq\n
        EN : Method to update the Groq API key
        """
        self.__groq.api_key = get_key('.env', 'GROQ_API_KEY')

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
        chat_completion = self.__groq.chat.completions.create(
            messages=[
                {"role": "system", "content": self.__prompt_request},
                {"role": "user", "content": request}
            ],
            model=self.__groq_model,
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
        chat_completion = self.__groq.chat.completions.create(
            messages=[
                {"role": "system", "content": self.__prompt_response},
                {"role": "user", "content": f"Question : {question}. Données de course : {data}"}
            ],
            model=self.__groq_model,
            temperature=0.5
        )
        return chat_completion.choices[0].message.content