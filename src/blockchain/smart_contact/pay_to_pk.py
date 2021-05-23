"""
File   : pay_to_pk.py
Author : ParisNeo
Description :
    Pay to the public key smart contract
"""
import pickle
import time

from base58 import scrub_input

from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode, verify, privateKey2Text, publicKey2Text
from blockchain.data.smart_contract import SmartContract

class P2PK(SmartContract):
    def __init__(self, id, timestamp, source_pk, dest_pk, signature):
        self.id = id
        self.timestamp = timestamp
        self.source_pk = source_pk
        self.dest_pk = dest_pk
        self.signature = signature

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
