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


from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode

class Block():
    def __init__(self, id = 0, ts = time.time(), coinbase=Transaction(),transactions=[], prevH=hash(b""), miner_private_key=generateKeys()[0]):
        """Every block has an ID, a timestamp, a coinbase transaction( that pays the miner), a list of regular transactions, a hash of the block
        and a validation by the signature of the miner

        Notice there is no nonce here as we don't require a proof of work :) We only use a proof of stake.
        """
        self.id = id,
        self.timestamp = ts
        self.coinbase = coinbase # This is a special transaction
        self.transactions = transactions
        self.prevH = prevH

        data = bytes(str(id)+str(id)+str(self.pending_transactions)+str(prevH),"utf8")
        self.hash = hash(data)

        # Asignature to tell that the block is signed by this user
        self.validation = sign(miner_private_key, data).decode('latin-1')
