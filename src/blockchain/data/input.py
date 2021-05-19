"""
File   : input.py
Author : ParisNeo
Description :
    Each transaction has multiple inputs and multiple outputs
    Inputs must be unspent money 
"""
from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode, verify, privateKey2Text, publicKey2Text

class Input():
    def __init__(self, private_key, public_key, amount):
        self.public_key = public_key
        self.amount = amount
        data = bytes(str(public_key)+str(amount),"utf8")
        self.signature = sign(private_key, data)
    
    def verify(self):
        data = bytes(str(self.public_key)+str(self.amount),"utf8")
        return verify(self.public_key, data, self.signature)        

    def __str__(self) -> str:
        return "\n".join([
            f"public key => {publicKey2Text(self.public_key)}",
            f"amount => {self.amount}",
            f"signature => {b58encode(self.signature)}"
        ])

    def serialize(self):
        return bytes(str(self.public_key)+str(self.amount),"utf8")