import requests
import os
from dotenv import load_dotenv


def send_email_brevo(to_email, subject, message_text):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": os.environ["TOKEN_BREVO"],
        "content-type": "application/json"
    }
    data = {
        "sender": {"name": "no_reply BDE Ensai", "email": os.environ["EMAIL_BREVO"]},
        "to": [{"email": to_email, "name": "Destinataire"}],
        "subject": subject,
        "textContent": message_text
    }

    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.text


if __name__ == "__main__":
    load_dotenv()

"""
    # Exemple d’utilisation
    status, response = send_email_brevo(
        to_email="projet.shotgun@gmail.com",
        subject="Hello depuis Brevo",
        message_text="Voici un email envoyé avec l'API de Brevo en Python !"
    )


    print("Statut :", status)
    print("Réponse :", response)
"""
