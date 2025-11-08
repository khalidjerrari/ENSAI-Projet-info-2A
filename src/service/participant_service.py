# service/participant_service.py
from typing import List, Optional

from dao.participant_dao import ParticipantDao
from model.participant_models import ParticipantModelIn, ParticipantModelOut


class ParticipantService:
    """
    Service pour la gestion des participants.
    Contient la logique métier et appelle le DAO correspondant.
    """

    def __init__(self):
        self.dao = ParticipantDao()

    # ---------- READ ----------
    def get_all_participants(self, limit: int = 100, offset: int = 0) -> List[ParticipantModelOut]:
        return self.dao.find_all(limit=limit, offset=offset)

    def get_participant_by_id(self, id_utilisateur: int) -> ParticipantModelOut:
        participant = self.dao.find_by_id(id_utilisateur)
        if not participant:
            raise ValueError(f"Aucun participant trouvé avec l'id {id_utilisateur}.")
        return participant

    def get_participant_by_email(self, email: str) -> ParticipantModelOut:
        participant = self.dao.find_by_email(email)
        if not participant:
            raise ValueError(f"Aucun participant trouvé avec l'email {email}.")
        return participant

    # ---------- CREATE ----------
    def create_participant(self, participant_in: ParticipantModelIn) -> ParticipantModelOut:
        # Vérifie si un participant existe déjà avec cet email
        existing = self.dao.find_by_email(participant_in.email)
        if existing:
            raise ValueError(f"L'email '{participant_in.email}' est déjà utilisé.")
        return self.dao.create(participant_in)

    # ---------- UPDATE ----------
    def update_participant(self, participant_out: ParticipantModelOut) -> ParticipantModelOut:
        existing = self.dao.find_by_id(participant_out.id_utilisateur)
        if not existing:
            raise ValueError("Impossible de mettre à jour : participant introuvable.")
        return self.dao.update(participant_out)

    # ---------- DELETE ----------
    def delete_participant(self, id_utilisateur: int) -> bool:
        existing = self.dao.find_by_id(id_utilisateur)
        if not existing:
            raise ValueError("Impossible de supprimer : participant introuvable.")
        return self.dao.delete(id_utilisateur)

    # ---------- AUTH ----------
    def authenticate_participant(self, email: str, mot_de_passe: str) -> ParticipantModelOut:
        participant = self.dao.authenticate(email, mot_de_passe)
        if not participant:
            raise ValueError("Email ou mot de passe incorrect.")
        return participant

    def change_participant_password(self, id_utilisateur: int, new_password: str) -> bool:
        existing = self.dao.find_by_id(id_utilisateur)
        if not existing:
            raise ValueError("Participant introuvable pour mise à jour du mot de passe.")
        return self.dao.change_password(id_utilisateur, new_password)
