from groq import Groq

groq_model = "llama3-70b-8192"
groq_api_key = "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"
prompt_request = (
    "Je suis un pilote de course en pleine compétition et tu es mon ingénieur de course."
    "À chaque question, réponds uniquement par la fonction correspondante selon le thème."
    "Thèmes et Fonctions :"
    "Ma Position : my_position"
    "Nombre de tours total dans la course : count_total_laps"
    "Nombre de tours restants dans la course : count_remaining_laps"
    "Durée totale de la course : duration_race"
    "Durée restante de la course : duration_remaining"
    "Mon meilleur temps au tour : my_best_lap_time"
    "Mon dernier temps au tour : my_last_lap_time"
    "Mon nombre d'incidents : incident_count"
    "Meilleur temps au tour de la voiture devant : best_lap_time_ahead_car"
    "Dernier temps au tour de la voiture devant : last_lap_time_ahead_car"
    "Meilleur temps au tour de la voiture derrière : best_lap_time_behind_car"
    "Dernier temps au tour de la voiture derrière : last_lap_time_behind_car"
    "Autorisation des pneus pluie : declared_wet"
    "Pourcentage de l'humidité : pourcentage_humidity"
    "Pourcentage de précipitation : pourcentage_precipitation"
    "Litres de carburant restant : remaining_litres_of_fuel"
    "Pourcentage de carburant restant : remaining_percentage_of_fuel"
    "Carburant manquant pour finir la course : get_fuel_necessary"
)


def send_request(groq, audio_text) -> str:
    chat_completion = groq.chat.completions.create(
        messages=[
            {"role": "system", "content": prompt_request},
            {"role": "user", "content": audio_text}
        ],
        model=groq_model,
    )
    return chat_completion.choices[0].message.content


class TextAI:
    def __init__(self):
        self.model = Groq(api_key=groq_api_key)

    def process_request(self, audioAI) -> str:
        audio_text = audioAI.transcribe_audio()
        return send_request(self.model, audio_text=audio_text)
