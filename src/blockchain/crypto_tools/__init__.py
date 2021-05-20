"""
"""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from base58 import b58encode, b58decode


# ================= cryptography helpers ======================================
def hash(data):
    """Hash some data
    """
    # Hash the stuff we need to hash
    digest = SHA256.new()
    digest.update(data)
    hash= digest.hexdigest()
    return hash

def generateKeys():
    private_key = RSA.generate(1024)
    public_key = private_key.public_key()
    return private_key, public_key

def sign(private_key:RSA.RsaKey, message):
    """Sign a message
    Parameters
    ----------
    private_key (RSAPublicKey)   : The private key to sign the message with
    message     (str)            : The message to be signed
    """
    hasher = SHA256.new(message)
    signer = PKCS1_v1_5.new(private_key)
    signature = signer.sign(hasher)
    return signature

def verify(public_key, message, signature):
    """Verify the message signature
    Parameters
    ----------
    public_key (RSAPublicKey)   : The public key to verify that the sender is the right one 
    message    (str)            : The signed message (used for verification)
    signature  (str)            : The signature
    """
    hasher = SHA256.new(message)
    verifier = PKCS1_v1_5.new(public_key)
    return verifier.verify(hasher, signature)



def privateKey2Text(key:RSA.RsaKey):
    """Converts a private key to text
    """
    return b58encode(key.exportKey('DER'))

def publicKey2Text(key:RSA.RsaKey):
    """Converts a public key to text
    """
    return b58encode(key.exportKey('DER'))


def text2PrivateKey(text:str):
    """Convert a text to a private key
    """
    return RSA.importKey(b58decode(text))

def text2PublicKey(text:str):
    """Convert a text to a key
    """
    return RSA.importKey(b58decode(text))

