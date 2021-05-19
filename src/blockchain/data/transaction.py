import pickle
import time

from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode, verify, privateKey2Text, publicKey2Text

class Transaction():
    def __init__(self, id = 0, timestamp = time.time(), inputs=[], outputs=[], signature=bytes([1] * 256)):
        self.id = id,
        self.timestamp = timestamp
        self.inputs = inputs
        self.outputs = outputs
        data = bytes(str(self.id) + str(self.timestamp)+ "\n".join([str(i.serialize()) for i in self.inputs])+ "\n".join([str(o.serialize()) for o in self.outputs]), "utf8")
        self.hash = hash(data)
        self.signature = signature

    def sign(self, private_key):
        data = bytes(str(self.id) + str(self.timestamp)+ "\n".join([str(i.serialize()) for i in self.inputs])+ "\n".join([str(o.serialize()) for o in self.outputs]), "utf8")
        self.signature = sign(private_key, data)

    def verify(self, miner_public_key):
        data = bytes(str(self.id) + str(self.timestamp)+ "\n".join([str(i.serialize()) for i in self.inputs])+ "\n".join([str(o.serialize()) for o in self.outputs]), "utf8")
        return verify(miner_public_key, data, self.signature)


    def __str__(self) -> str:
        return str(self.id)+str(self.timestamp)+str(self.inputs)+str(self.outputs)+str(self.signature)
