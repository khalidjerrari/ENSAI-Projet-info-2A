# utils/password_utils.py
import bcrypt
from typing import Optional
from getpass import getpass


def hash_password(password: str, rounds: int = 12, salt: Optional[bytes] = None) -> str:
    """
    Hash un mot de passe avec bcrypt.
    - rounds : facteur de coût (par défaut 12).
    - salt : sel bcrypt optionnel (généralement on laisse None pour bcrypt.gensalt()).

    Retourne une chaîne UTF-8 au format bcrypt, ex: $2b$12$...
    """
    if isinstance(password, str):
        password = password.encode("utf-8")

    if salt is None:
        salt = bcrypt.gensalt(rounds=rounds)

    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode("utf-8")


def verify_password(stored_hash: str, password: str) -> bool:
    """
    Vérifie si le mot de passe correspond au hash bcrypt stocké.
    Retourne True si OK, False sinon.
    """
    try:
        if isinstance(password, str):
            password = password.encode("utf-8")
        return bcrypt.checkpw(password, stored_hash.encode("utf-8"))
    except Exception:
        return False


# --- Utilitaire CLI simple ---
def _cli_hash_interactive():
    """Saisie interactive (masquée) pour hasher un mot de passe et l'afficher."""
    print("Générateur de hash bcrypt")
    pwd = getpass("Mot de passe à hasher : ")
    pwd2 = getpass("Confirmation : ")
    if pwd != pwd2:
        print("Les mots de passe ne correspondent pas. Abandon.")
        return
    hashed = hash_password(pwd)
    print("\nHash (à stocker en base) :")
    print(hashed)


def _cli_hash_from_args(passwords):
    """Hash une liste de mots de passe passés en argument et les affiche."""
    for p in passwords:
        h = hash_password(p)
        print(h)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Utilitaire pour hasher des mots de passe (bcrypt)."
    )
    parser.add_argument(
        "-p", "--password",
        action="append",
        help="Mot de passe à hasher (danger : apparaît dans l'historique shell). Répéter pour plusieurs."
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Mode interactif (saisie masquée)."
    )
    parser.add_argument(
        "-c", "--cost",
        type=int,
        default=12,
        help="Facteur de coût bcrypt (rounds), défaut 12."
    )
    args = parser.parse_args()

    if args.interactive:
        _cli_hash_interactive()
    elif args.password:
        # Permettre de spécifier le coût depuis la CLI
        for p in args.password:
            print(hash_password(p, rounds=args.cost))
    else:
        parser.print_help()

# Exemple :
# PYTHONPATH="src"; python src/utils/securite.py -p mdpAlice123 -p mdpBob123 -p mdpMarieMart1