from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
import os

RSA_PRIVATE_KEY_FILE = os.path.join("rsa_keys", "private.pem")
RSA_PUBLIC_KEY_FILE = os.path.join("rsa_keys", "public.pem")

def encrypt_file_with_aes_and_rsa(data):
    try:
        aes_key = get_random_bytes(32)
        cipher = AES.new(aes_key, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        with open(RSA_PUBLIC_KEY_FILE, 'rb') as f:
            rsa_public_key = RSA.import_key(f.read())
        encrypted_aes_key = PKCS1_OAEP.new(rsa_public_key).encrypt(aes_key)

        return encrypted_aes_key + cipher.nonce + tag + ciphertext
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def decrypt_file_with_aes_and_rsa(encrypted_data):
    try:
        encrypted_aes_key, nonce, tag, ciphertext = (
            encrypted_data[:256], 
            encrypted_data[256:272], 
            encrypted_data[272:288], 
            encrypted_data[288:]
        )

        with open(RSA_PRIVATE_KEY_FILE, 'rb') as f:
            rsa_private_key = RSA.import_key(f.read())
        aes_key = PKCS1_OAEP.new(rsa_private_key).decrypt(encrypted_aes_key)

        cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)
    except Exception as e:
        print(f"Decryption error: {e}")
        return None