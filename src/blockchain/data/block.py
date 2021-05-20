"""
File   : block.py
Author : ParisNeo
Description :
    The block chain is a chain of blocks. Here is a class that describes a single block in our block chain
    A block is a hata holder that contains a list of signed transactions with a
"""
import pickle
import time
from .transaction import Transaction


from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode, verify
import pickle
from pathlib import Path

class Block():
    def __init__(self, id = 0, ts = time.time(), coinbase=Transaction(),transactions=[], prevH=hash(b"")):
        """Every block has an ID, a timestamp, a coinbase transaction( that pays the miner), a list of regular transactions, a hash of the block
        and a validation by the signature of the miner

        Notice there is no nonce here as we don't require a proof of work :) We only use a proof of stake.
        """
        self.id = id
        self.timestamp = ts
        self.coinbase = coinbase # This is a special transaction
        self.transactions = transactions
        self.prevH = prevH

        data = bytes(str(id)+str(self.transactions)+str(prevH),"utf8")
        self.hash = hash(data)
        self.signature = hash(b"")

    def sign(self, miner_private_key):
        """Sign the block
        """
        # Asignature to tell that the block is signed by this user
        data = bytes(str(self.id)+"\n".join([str(t.serialize()) for t in self.transactions])+str(self.prevH),"utf8")
        self.signature = sign(miner_private_key, data)

    def verify(self, miner_public_key):
        """Verify the block
        """
        data = bytes(str(self.id)+"\n".join([str(t.serialize()) for t in self.transactions])+str(self.prevH),"utf8")
        return verify(miner_public_key, data, self.signature)

    def save(self, block_chain_path):
        """Save the block
        """
        block_chain_path = Path(block_chain_path)
        with open(str(block_chain_path/f"{self.id}.pkl"),"wb") as f:
            pickle.dump(self,f)


    def load(self, block_chain_path, block_id):
        """Save the block
        """
        block_chain_path = Path(block_chain_path)
        with open(str(block_chain_path/f"{block_id}.pkl"),"rb") as f:
            v = pickle.load(f)
            self.id = v.id,
            self.timestamp = v.timestamp
            self.coinbase = v.coinbase # This is a special transaction
            self.transactions = v.transactions
            self.prevH = v.prevH
            self.hash = v.hash
            self.signature = v.signature
