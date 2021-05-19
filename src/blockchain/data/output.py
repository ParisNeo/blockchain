"""
File   : output.py
Author : ParisNeo
Description :
    Each transaction has multiple inputs and multiple outputs
    Inputs must be unspent money 
"""

from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode, verify, privateKey2Text, publicKey2Text

class Output():
    def __init__(self, public_key, amount):
        self.public_key = public_key
        self.amount = amount
    
    def __str__(self) -> str:
        return "\n".join([
            f"public key => {publicKey2Text(self.public_key)}",
            f"amount => {self.amount}"
        ])


    def serialize(self):
        return bytes(str(self.public_key)+str(self.amount),"utf8")