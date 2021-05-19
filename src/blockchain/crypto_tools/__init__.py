"""
"""
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from base58 import b58encode, b58decode


# ================= cryptography helpers ======================================
def hash(data):
    """Hash some data
    """
    # Hash the stuff we need to hash
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data)
    hash= digest.finalize()
    return hash

def generateKeys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=512)
    public_key = private_key.public_key()
    return private_key, public_key

def sign(private_key, message):
    """Sign a message
    Parameters
    ----------
    private_key (RSAPublicKey)   : The private key to sign the message with
    message     (str)            : The message to be signed
    """
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )      

def verify(public_key, message, signature):
    """Verify the message signature
    Parameters
    ----------
    public_key (RSAPublicKey)   : The public key to verify that the sender is the right one 
    message    (str)            : The signed message (used for verification)
    signature  (str)            : The signature
    """
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )  
        return True
    except InvalidSignature as inv_signature:
        return False



def privateKey2Text(key):
    """Converts a private key to text
    """
    return "".join(key.private_bytes(
                                encoding=serialization.Encoding.PEM,
                                format=serialization.PrivateFormat.PKCS8,
                                encryption_algorithm=serialization.NoEncryption()
                            ).decode("utf8")[len("-----BEGIN PRIVATE KEY-----")+1:-len("-----END PRIVATE KEY-----")-2].split("\n"))

def publicKey2Text(key):
    """Converts a public key to text
    """
    return "".join(key.public_bytes(
                                encoding=serialization.Encoding.PEM,
                                format=serialization.PublicFormat.SubjectPublicKeyInfo
                            ).decode("utf8")[len("-----BEGIN PUBLIC KEY-----")+1:-len("-----END PUBLIC KEY-----")-2].split("\n"))


def text2PrivateKey(text):
    """Convert a text to a private key
    """
    return serialization.load_pem_private_key(bytes("-----BEGIN PRIVATE KEY-----\n"+text+"\n-----END PRIVATE KEY-----","utf8"))

def text2PublicKey(text):
    """Convert a text to a key
    """
    txt_bytes = bytes("-----BEGIN PUBLIC KEY-----\n"+text+"\n-----END PUBLIC KEY-----","utf8")
    return serialization.load_pem_public_key(txt_bytes)

