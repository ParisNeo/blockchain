"""
File   : block.py
Author : ParisNeo
Description :
    The block chain is a chain of blocks. Here is a class that describes a single block in our block chain
"""
import pickle
import time
from blockchain.data import transaction

class MemPool():
    def __init__(self):
        self.transactions=[]
