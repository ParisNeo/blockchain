# Project       : BlockChain
# Script        : core.py
# Author        : ParisNeo
# Description   : The core code for the blockchain project

from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidSignature
import pickle
from datetime import datetime
import web3

class BlockChain():
    """ Main class
    """
    
    def __init__(
                    self, 
                    miner_private_key=rsa.generate_private_key(key_size=4096), 
                    ledger_file_name="./ledger.pkl", 
                    pending_transactions_file_name="./pending.pkl", 
                    root_key_store_file="./root_key.pkl" 
                ):
        """Initialises the blockchain object
        Parameters
        ----------
        miner_public_key (RSAPrivateKey): the miner public key object
        miner_public_key (RSAPrivateKey): the miner public key object
        ledger_file_name  (Path or str): the name of the file containing the ledger
        """
        # Save keys in memory
        self.miner_public_key = miner_private_key
        self.miner_private_key = miner_private_key

        # Save ledger and pending transaction files
        self.ledger_file_name = Path(ledger_file_name)
        self.pending_transactions_file_name = Path(pending_transactions_file_name)

        # If the 
        if self.pending_transactions_file_name.exists():
            self.pending_transactions = pickle.load(open(str(self.pending_transactions_file_name),"rb"))
        else:
            self.pending_transactions = []

        # If the ledger file exists, load it
        if self.ledger_file_name.exists():
            self.ledger = pickle.load(open(str(self.ledger_file_name),"rb"))
        # If not, create it
        else:
            # Build root acount, the trillionaire of this block chain that should start giving money for free to bootstrap the ledger work
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            public_key = private_key.public_key()


            # save the key very carefully, otherwize it will be lost
            pickle.dump(private_key, open(root_key_store_file,'wb')) 

            #Build a ledger with a first virtual transaction to the root id
            ts = datetime.now().timestamp()

            # Hash the stuff we need to hash
            digest = hashes.Hash(hashes.SHA256())
            digest.update(bytes(str(ts)+str(public_key)+str(public_key)))
            hash= digest.finalize()

            # Build ledger entry
            entry = {
                    "timestamp":ts,
                    "sender":0,# A dump root sender that is used just to create the stuff
                    "sender_validation":private_key.sign(hash),
                    "receiver":public_key,
                    "amount":100000000000, # The maximum amount of coins for this blockchain
                    "Hash":hash,
                    "Validation":private_key.sign(hash)
                }
            self.ledger=[
                entry
            ]
            pickle.dump(self.ledger,open(str(self.ledger_file_name),"wb"))
        
    def push_transaction(self, ts, sender_key, sender_val, receiver_key, amount):
        # check that the sender has something in its wallet
        sender_money = 0
        for entry in self.ledger:
            if entry["receiver"]==sender_key:
                sender_money += entry["amount"]
            if entry["sender"]==sender_key:
                sender_money -= entry["amount"]
        # Now we know how much the sender have. let's check if he can actually send the money to the receiver
        if sender_money<amount:
            return False # Refuse transaction
        else:# Transaction is ok let's validate it
            # the sender cyphers this code using his private key, and put it in sender_val parameter
            #to verify this we use his public key. if we can decode 
            digest = hashes.Hash(hashes.SHA256())
            digest.update(bytes(str(ts)+str(sender_key)+str(receiver_key)+str(amount)))
            validation_code= digest.finalize()

            # Verify that the sender is the right sender
            try:
                sender_key.verify(
                    validation_code,
                    sender_val
                    )
                print('valid!')
            except InvalidSignature:
                print('invalid!')
                return False

            pending_entry = {
                "timestamp":ts,
                "sender":sender_key,# A dump root sender that is used just to create the stuff
                "sender_validation":sender_val, # the sender must sign the amount of money he wants to send using his private key 
                "receiver":receiver_key,
                "amount":amount, # The maximum amount of coins for this blockchain
            }
            self.pending_transactions.append(pending_entry)
            return True
        
    def validate_transactions(self):
        """Validates all pending transactions
        """
        #Build a ledger with a first virtual transaction to the root id
        # This is validation timestamp
        ts = datetime.now().timestamp()

        
        for pending_transaction in self.pending_transactions:
            # Hash the stuff we need to hash
            digest = hashes.Hash(hashes.SHA256())
            digest.update(bytes(str(ts)+str(pending_transaction["sender"])+str(pending_transaction["receiver_key"])+str(pending_transaction["amount"])))
            hash= digest.finalize()
            # Build ledger entry
            entry = {
                    "timestamp":pending_transaction["ts"],
                    "sender":pending_transaction["sender"],# A dump root sender that is used just to create the stuff
                    "receiver":pending_transaction["receiver_key"],
                    "amount":pending_transaction["amount"], # The maximum amount of coins for this blockchain
                    "Hash":hash,
                    "Validation":self.miner_private_key.sign(hash)
                }
            # Add it to the ledger
            self.ledger.append(entry)
