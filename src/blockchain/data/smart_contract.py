"""
File   : smart_contract.py
Author : ParisNeo
Description :
    A smart contract to be implemented and registered to the block chain with a register_smart_contract transaction
"""
import pickle
import time

from base58 import scrub_input

from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode, verify, privateKey2Text, publicKey2Text
from blockchain.data.smart_contract import SmartContract
class SmartContract():
    def __init__(self, id = 0, timestamp = time.time()):
        self.id = id
        self.timestamp = timestamp
        data = self.serialize()
        self.hash = hash(data)

    def sign(self, private_key):
        raise Exception("Unimplemented")

    def verify(self, miner_public_key):
        raise Exception("Unimplemented")


    def serialize(self):
        """ Should return a binary representation of the code
        """
        return pickle.dumps(self)


    def __str__(self) -> str:
        return str(self.id)+str(self.timestamp)+str(self.inputs)+str(self.outputs)+str(self.signature)
