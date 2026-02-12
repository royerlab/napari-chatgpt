"""Password-protected encrypted storage for LLM API keys.

Keys are encrypted with Fernet (AES-128-CBC + HMAC-SHA256) using a
password-derived key (PBKDF2-HMAC-SHA256, 390 000 iterations). Each
key is stored as a JSON file under ``~/.omega_api_keys/``.
"""

import base64
import json
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Legacy salt for backward compatibility with existing keys
_LEGACY_SALT = b"123456789"


class KeyVault:
    """Encrypted vault for a single API key, persisted as a JSON file.

    Attributes:
        keys_file: Path to the JSON file storing the encrypted key.
    """

    def __init__(self, key_name: str, folder_path: str = "~/.omega_api_keys"):
        """Create a vault for the given key name.

        Args:
            key_name: Logical name used as the JSON filename stem.
            folder_path: Directory in which to store encrypted key files.
        """
        # Define the path to the directory where the key file will be stored
        keys_dir = os.path.expanduser(folder_path)

        # Create the directory if it doesn't already exist
        os.makedirs(keys_dir, exist_ok=True)

        # Define the path to the key file
        self.keys_file = os.path.join(keys_dir, f"{key_name}.json")

    def clear_key(self):
        """Delete the encrypted key file from disk, if it exists."""
        try:
            os.remove(self.keys_file)
        except OSError:
            pass

    def write_api_key(self, api_key: str, password: str) -> str:
        """Encrypt and persist an API key protected by a password.

        Args:
            api_key: The plaintext API key to store.
            password: Password used to derive the encryption key.

        Returns:
            The base64-encoded ciphertext written to disk.
        """
        # Generate a random salt for new keys (16 bytes)
        salt = os.urandom(16)

        cipher_suite = Fernet(_normalise_password(password, salt=salt))

        # Write the encrypted key to the file
        with open(self.keys_file, "w") as f:
            # Compute encrypted key:
            encrypted_key = _encode64(cipher_suite.encrypt(bytes(api_key, "ascii")))

            # Create a dictionary containing the encrypted key and salt
            data = {"api_key": encrypted_key, "salt": _encode64(salt)}

            # Write the dictionary to the file
            json.dump(data, f)

            return encrypted_key

    def is_key_present(self) -> bool:
        """Check whether an encrypted key file exists and is non-empty."""
        try:
            with open(self.keys_file) as f:

                # Load the dictionary from the file
                data = json.load(f)

                # Check if key is present:
                return data["api_key"] is not None and len(data["api_key"]) > 0
        except FileNotFoundError:
            return False

    def read_api_key(self, password: str) -> str:
        """Decrypt and return the stored API key.

        Args:
            password: The password used when the key was written.

        Returns:
            The plaintext API key.

        Raises:
            cryptography.fernet.InvalidToken: If the password is incorrect.
            FileNotFoundError: If no key file exists.
        """
        with open(self.keys_file) as f:
            # Load the dictionary from the file
            data = json.load(f)

            # Check if salt exists (new format) or use legacy salt (backward compat)
            if "salt" in data:
                salt = _decode64(data["salt"], to_string=False)
            else:
                salt = _LEGACY_SALT

            cipher_suite = Fernet(_normalise_password(password, salt=salt))

            # Get the encrypted key from the dictionary
            encrypted_key = _decode64(data["api_key"], to_string=False)

            # Decrypt the key using the Fernet instance
            api_key = cipher_suite.decrypt(encrypted_key).decode()

            return api_key


def _normalise_password(password: str, salt: bytes):
    """Derive a Fernet-compatible key from a password and salt via PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(bytes(password, "ascii")))

    return key


def _encode64(message: str | bytes):
    """Base64-encode a string or bytes, returning an ASCII string."""
    if type(message) == str:
        message = message.encode("ascii")

    base64_bytes = base64.b64encode(message)
    base64_message = base64_bytes.decode("ascii")
    return base64_message


def _decode64(message_b64: str, to_string: bool = True):
    """Decode a base64-encoded ASCII string, optionally returning bytes."""
    base64_bytes = message_b64.encode("ascii")
    message = base64.b64decode(base64_bytes)
    if to_string:
        message = message.decode("ascii")
    return message
