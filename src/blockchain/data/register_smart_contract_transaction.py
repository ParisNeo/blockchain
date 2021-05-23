"""
File   : register_smart_contract_transaction.py
Author : ParisNeo
Description :
    A special transaction that resisters a smart contract to the blockchain
"""
import pickle
import time

from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode, verify, privateKey2Text, publicKey2Text
from blockchain.data.smart_contract import SmartContract
class RegisterSCT():
    def __init__(self, id = 0, timestamp = time.time(), sc:SmartContract=SmartContract(), signature=bytes([1] * 256)):
        self.id = id
        self.timestamp = timestamp
        self.sc = sc
        data = self.serialize()
        self.hash = hash(data)
        self.signature = signature

    def sign(self, private_key):
        data = self.serialize()
        self.signature = sign(private_key, data)

    def verify(self, miner_public_key):
        # Here the transaction is valid, but we need to verify the miner signature        
        data = self.serialize()
        return verify(miner_public_key, data, self.signature)

    def serialize(self):
        id_= bytes(str(self.id), "utf8")
        timestamp_  = bytes(str(self.timestamp),"utf8")
        sc_     = self.sc

        return id_ + timestamp_ + sc_

    def __str__(self) -> str:
        return str(self.id)+str(self.timestamp)+str(self.inputs)+str(self.outputs)+str(self.signature)
