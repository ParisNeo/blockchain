"""
File   : transaction.py
Author : ParisNeo
Description :
    Main class for a many to many coin transfert transaction
    Smart contracts are codes that inherit from this class and should implement the sign and verify 
"""
import pickle
import time

from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode, verify, privateKey2Text, publicKey2Text

class Transaction():
    def __init__(self, id = 0, timestamp = time.time(), inputs=[], outputs=[], signature=bytes([1] * 256)):
        self.id = id
        self.timestamp = timestamp
        self.inputs = inputs
        self.outputs = outputs
        data = self.serialize()
        self.hash = hash(data)
        self.signature = signature

    def sign(self, private_key):
        data = self.serialize()
        self.signature = sign(private_key, data)

    def verify(self, miner_public_key):
        # First verify that every input in this transaction is valid
        input_size = 0
        for input in self.inputs:
            if not input.verify():
                return False
            input_size += input.amount
        # Then verify that what we have in input and output is the same
        output_size = 0
        for output in self.outputs:
            output_size += output.amount
        if input_size!=output_size:
            return False
        # Here the transaction is valid, but we need to verify the miner signature        
        data = bytes(str(self.id) + str(self.timestamp)+ "\n".join([str(i.serialize()) for i in self.inputs])+ "\n".join([str(o.serialize()) for o in self.outputs]), "utf8")
        return verify(miner_public_key, data, self.signature)

    def serialize_inputs(self):
        return bytes("\n".join([str(i.serialize()) for i in self.inputs]),"utf8")
    def serialize_outputs(self):
        return bytes("\n".join([str(o.serialize()) for o in self.outputs]),"utf8")

    def serialize(self):
        id_= bytes(str(self.id), "utf8")
        timestamp_  = bytes(str(self.timestamp),"utf8")
        inputs_     = self.serialize_inputs()
        outputs_     = self.serialize_outputs()

        return id_ + timestamp_ + inputs_ + outputs_

    def __str__(self) -> str:
        return str(self.id)+str(self.timestamp)+str(self.inputs)+str(self.outputs)+str(self.signature)
