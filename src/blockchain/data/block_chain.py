"""
File   : block_chain.py
Author : ParisNeo
Description :
    A chain of blocks stored on disk as pkl files
"""
import pickle
import time
from .block import Block


from blockchain.crypto_tools import hash, sign, generateKeys, b58encode, b58decode, verify
import pickle

class BlockChain():
    def __init__(self, path="./ledgers/ledger"):
        self.curr_block = Block()