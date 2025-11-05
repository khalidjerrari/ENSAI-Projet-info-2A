# utils/password_utils.py
import hashlib
import os
import binascii
import secrets
from typing import Optional
from getpass import getpass

# Paramètres recommandés (ajustables)
PBKDF2_ITERATIONS = 260_000
SALT_BYTES = 16
DKLEN = 32  # 32 bytes = 256 bits

PBKDF2_PREFIX = "pbkdf2$sha256"


def _generate_salt(n: int = SALT_BYTES) -> bytes:
    """Génère un sel aléatoire en bytes."""
    return os.urandom(n)


def hash_password(password: str, iterations: int = PBKDF2_ITERATIONS, salt: Optional[bytes] = None) -> str:
    """
    Hash un mot de passe en utilisant PBKDF2-HMAC-SHA256.
    Retourne une chaîne au format : pbkdf2$sha256$<iterations>$<salt_hex>$<dk_hex>
    """
    if salt is None:
        salt = _generate_salt()
    if isinstance(password, str):
        password = password.encode("utf-8")

    dk = hashlib.pbkdf2_hmac("sha256", password, salt, iterations, dklen=DKLEN)
    salt_hex = binascii.hexlify(salt).decode("ascii")
    dk_hex = binascii.hexlify(dk).decode("ascii")
    return f"{PBKDF2_PREFIX}${iterations}${salt_hex}${dk_hex}"


def verify_password(stored_hash: str, password: str) -> bool:
    """
    Vérifie si le mot de passe correspond au hash stocké (format pbkdf2$sha256$...).
    Retourne True si OK, False sinon.
    """
    try:
        parts = stored_hash.split("$")
        if len(parts) != 5 or parts[0] != "pbkdf2" or parts[1] != "sha256":
            return False
        iterations = int(parts[2])
        salt = binascii.unhexlify(parts[3])
        dk_stored = binascii.unhexlify(parts[4])
    except Exception:
        return False

    if isinstance(password, str):
        password = password.encode("utf-8")

    dk_check = hashlib.pbkdf2_hmac("sha256", password, salt, iterations, dklen=len(dk_stored))
    return secrets.compare_digest(dk_check, dk_stored)


# --- Utilitaire CLI simple ---
def _cli_hash_interactive():
    """Saisie interactive (masquée) pour hasher un mot de passe et l'afficher."""
    print("Générateur de hash PBKDF2-HMAC-SHA256")
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

    parser = argparse.ArgumentParser(description="Utilitaire pour hasher des mots de passe (PBKDF2-HMAC-SHA256).")
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
    args = parser.parse_args()

    if args.interactive:
        _cli_hash_interactive()
    elif args.password:
        _cli_hash_from_args(args.password)
    else:
        parser.print_help()

#PYTHONPATH="src"; python src/utils/securite.py -p mdpAlice123 -p mdpBob123