from Crypto.PublicKey import RSA
import os

def generate_rsa_key_pair():
    if not os.path.exists("rsa_keys"):
        os.makedirs("rsa_keys")

    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    with open("rsa_keys/private.pem", 'wb') as priv_file:
        priv_file.write(private_key)

    with open("rsa_keys/public.pem", 'wb') as pub_file:
        pub_file.write(public_key)

generate_rsa_key_pair()
print("RSA keys generated successfully.")
