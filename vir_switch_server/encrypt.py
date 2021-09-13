from cryptography.fernet import Fernet


class Crypt:
    key = b'8tnFL71voDHkQ3V7XySswRC2ZHOIfB7lDt11n4OieQQ='

    @staticmethod
    def encrypt(msg_to_send: list) -> bytes:
        encoded_msg = str(msg_to_send).encode()
        pack_to_send = Fernet(Crypt.key).encrypt(encoded_msg)
        return pack_to_send

    @staticmethod
    def decrypt(pack_received: bytes) -> list:
        decoded_msg = Fernet(Crypt.key).decrypt(pack_received)
        msg_received = eval(decoded_msg.decode())
        return msg_received

