"""
File   : mempool.py
Author : ParisNeo
Description :
    Here are stored the pending transactions
"""
import pickle
import time
from blockchain.data import transaction

class MemPool():
    def __init__(self):
        self.transactions=[]
