import base64
import json
import os
from typing import Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class KeyVault:

    def __init__(self, key_name: str, folder_path: str = "~/.omega_api_keys"):

        # Define the path to the directory where the key file will be stored
        keys_dir = os.path.expanduser(folder_path)

        # Create the directory if it doesn't already exist
        os.makedirs(keys_dir, exist_ok=True)

        # Define the path to the key file
        self.keys_file = os.path.join(keys_dir, f"{key_name}.json")

    def clear_key(self):
        try:
            os.remove(self.keys_file)
        except OSError:
            pass

    def write_api_key(self, api_key: str, password: str) -> str:

        cipher_suite = Fernet(_normalise_password(password))

        # Write the encrypted key to the file
        with open(self.keys_file, "w") as f:
            # Compute encrypted key:
            encrypted_key = _encode64(
                cipher_suite.encrypt(bytes(api_key, 'ascii')))

            # Create a dictionary containing the encrypted key
            data = {
                "api_key": encrypted_key}

            # Write the dictionary to the file
            json.dump(data, f)

            return encrypted_key

    def is_key_present(self) -> bool:

        try:
            with open(self.keys_file, "r") as f:

                # Load the dictionary from the file
                data = json.load(f)

                # Check if key is present:
                return data["api_key"] is not None and len(data["api_key"]) > 0
        except FileNotFoundError:
            return False

    def read_api_key(self, password: str) -> str:
        cipher_suite = Fernet(_normalise_password(password))

        with open(self.keys_file, "r") as f:
            # Load the dictionary from the file
            data = json.load(f)

            # Get the encrypted key from the dictionary
            encrypted_key = _decode64(data["api_key"], to_string=False)

            # Decrypt the key using the Fernet instance
            api_key = cipher_suite.decrypt(encrypted_key).decode()

            return api_key


def _normalise_password(password: str, salt: bytes = b'123456789'):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )

    key = base64.urlsafe_b64encode(kdf.derive(bytes(password, 'ascii')))

    return key


def _encode64(message: Union[str, bytes]):
    if type(message) == str:
        message = message.encode('ascii')

    base64_bytes = base64.b64encode(message)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


def _decode64(message_b64: str, to_string: bool = True):
    base64_bytes = message_b64.encode('ascii')
    message = base64.b64decode(base64_bytes)
    if to_string:
        message = message.decode('ascii')
    return message
