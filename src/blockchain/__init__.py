# Project       : BlockChain
# Script        : core.py
# Author        : ParisNeo
# Description   : The core code for the blockchain project

from pathlib import Path
from blockchain.crypto_tools import sign, verify, publicKey2Text, hash
from blockchain.data.block_chain import BlockChain
from blockchain.p2p.gossip_net import GossipNode, GossipFrame
from blockchain.data import Block, BlockChain, Transaction
import random
import pickle
from datetime import datetime
import sys, traceback


class BCN_GossipEvents_():
    """List of acceptable events for gossip network
    """
    def __init__(self):
        """List of acceptable events for gossip network
        """
        self._GossipEvents={
            "HELLO":0,
            "GET_LEDGER_INFOS":1,
            "LEDGER_INFOS":2,
            "GET_LEDGER_BLOCK":3,
            "LEDGER_BLOCK":4,
        }

    def __getitem__(self, key):
        """A function to access the configuration using obj["key"]
        """
        return self._GossipEvents[key]

    def __getattr__(self, key):
        """A function to access the settings directly using obj.key
        """
        return self._GossipEvents[key]

BCN_GossipEvents = BCN_GossipEvents_()


class BlockChainNode(GossipNode):
    """ Main class
    Manages the local ledger, synchronizes it with the rest of the network, decides who can mine, receives transactions requests 
    """
    
    def __init__(
                    self, 

                    miner_private_key,
                    miner_public_key,

                    server_nick_name="Miner",
                    server_address="127.0.0.1",
                    server_port=44444,

                    ntp_server_address = 'europe.pool.ntp.org',

                    known_nodes_file_name="nodes.txt",
                    ledger_dir="./ledgers/ledger", 
                    pending_transactions_file_name="./pending.pkl", 
                    root_key_store_file="./root_key.rsa",
                    root_key_pass_phrase="password",


                    mining_coinbase_retribution=60,
                    mining_transaction_fee=0,
                    mining_cap=-1
                ):

        """Initialises the blockchain object

        Parameters
        ----------
        miner_private_key       (RSAPrivateKey)     : the miner private key object to sign stuff
        miner_public_key        (RSAPublicKey)      : the miner public key object to validate stuff

        server_nick_name        (str)               : Local server name
        server_address          (str)               : Local server address of the node
        server_port             (int)               : Local server port

        ntp_server_address      (str)               : Address of the NTP server to eep time synced over the network


        known_nodes_file_name   (str or Path)       : a file containing nodes of the network to which we try to connect for the federated decentralyzed network
        ledger_dir              (Path or str)       : the path to the ledger folder in which the ledger blocks are stored

        pending_transactions_file_name(Path or str) : A file to store the pending transactions in case of loss 
        root_key_store_file     (Path or str)       : A file to store the root key if this is the first of the first node (when you want to build a new network)
        root_key_pass_phrase    (Path or str)       : A passphrase to secure the file containing the root key pairs
        mining_coinbase_retribution      (float)    : Number of coins to give the validator for validating a block
        mining_transaction_fee  (float)             : Transaction fee to give the validator from the transactions to be validated (in factions, like 0.001 for example) put 0 for no fee transactions
        mining_cap              (float)             : The maximum amount of coins that could be mined (-1 for unlimited coin generation)
        """
        # Not ready yet to interact with the system until I am synced
        self.ready = False

        # List of blocks to request from the peer
        self.blocks_to_request=[]
        
        self.mining_coinbase_retribution = mining_coinbase_retribution
        self.mining_transaction_fee = mining_transaction_fee
        self.mining_cap = mining_cap

        # Save ledger and pending transaction files
        self.ledger_dir = Path(ledger_dir)
        self.pending_transactions_file_name = Path(pending_transactions_file_name)

        # If the pending transaction file exists, then load it
        if self.pending_transactions_file_name.exists():
            self.pending_transactions = pickle.load(open(str(self.pending_transactions_file_name),"rb"))
        else:
            self.pending_transactions = []

        # Build connection to p2p gossip network
        GossipNode.__init__(
                    self, 

                    miner_private_key,
                    miner_public_key,

                    server_nick_name="Miner",
                    server_address="127.0.0.1",
                    server_port=44444,

                    ntp_server_address = 'europe.pool.ntp.org',

                    known_nodes_file_name="nodes.txt",
        )


        # ==============================================
        # Data loading either from a backup file, if the network is completely off or from a peer who is alife
        # ==============================================

        # If the ledger file exists, load it and carry on
        if len(self.connected_peers)==0: # I am the only one !!
            bad_block = self.check_ledger_integrity()
            # if we managed to connect to some nodes, we can ask about the current status of the blockchain
            if bad_block==0:
                self.build_new_legder()
        # If not, create it (only for new networks)
        else:
            self.ledger_dir.mkdir(parents=True, exist_ok=True)
            self.build_new_legder()

    def process(self, node, data):
        """ Process to be done by the inheriting class
        """
        if data.type==BCN_GossipEvents.GET_LEDGER_INFOS:
            print(f"[Gossip packet] Received legder infos request from {node}")
            blocks_list = sorted([int(str(b.stem)) for b in self.ledger_dir.iterdir() if str(b.stem).isnumeric()])
            node.socket.send(
                    pickle.dumps(
                    GossipFrame(
                        BCN_GossipEvents.LEDGER_INFOS,
                        blocks_list[-1]
                    )
                    )
                )
                
            print(f"[Gossip packet] Sent ledger ingfos to {node}")
        elif data.type==BCN_GossipEvents.LEDGER_INFOS:
            print(f"Ledger infos {data.metadata}")
            blocks_list = [int(str(b.stem)) for b in self.ledger_dir.iterdir() if str(b.stem).isnumeric()]
            local_ledger_blocks = sorted(blocks_list)
            remote_ledger_last_block = data.metadata
            if len(local_ledger_blocks)==0: # I have no ledger or what so ever
                self.blocks_to_request= range(remote_ledger_last_block)
            else:
                if remote_ledger_last_block==0:# I am better than him got a longer chain
                    #TODO :notify that we have a longer chain
                    pass
                else:
                    # Prepare to ask for all those blocks
                    self.blocks_to_request = range(local_ledger_blocks[-1],remote_ledger_last_block)
                    pass

            if len(self.blocks_to_request)>0:
                # Request a ledger block
                print(f"[Gossip request] Requesting block {self.blocks_to_request[0]}")
                node.socket.send(
                        pickle.dumps(
                        GossipFrame(
                            BCN_GossipEvents.GET_LEDGER_BLOCK,
                            self.blocks_to_request[0]
                        )
                        )
                    )
            else:
                print(f"[Notification] Ready to process")
                self.ready=True
            # Find the tip of the ledger and ask for all new blocks
        elif data.type==BCN_GossipEvents.LEDGER_INFOS:
            # Tofdo ,send the requested ledger block
            pass


    def build_new_legder(self):
            # Consider this miner as the root of the ledger. Build the new network
            net_id = random.randint(0,2000000000)
            txt_sender_key = publicKey2Text(self.miner_public_key)
            txt_receiver_key = publicKey2Text(self.miner_public_key)
            self.pending_transactions=[]
            
            self.ledger=[
                self.validateBlock(0,"0")
            ]

    def validateBlock(self, id, prev):
            #Build a ledger with a first virtual transaction to the root id
            ts = datetime.now().timestamp()
            # Coinbase pays the miners
            coinbase = {
                            "amount":self.mining_coinbase_retribution,
                            "dest":publicKey2Text(self.miner_public_key)
                        }
            data = bytes(str(ts)+str(coinbase)+str(self.pending_transactions)+prev,"utf8")
            hash_ = hash(data)
            # Build ledger entry
            block = {
                    "blockID":id,
                    "timestamp":ts,
                    "Coinbase":coinbase,
                    "Transactions":self.pending_transactions,
                    "prev":prev,
                    "hash":hash_,
                    "Validation":sign(self.miner_private_key, data).decode('latin-1')
                }
            # Save the block
            pickle.dump(block, open(self.ledger_dir/str(id),"wb"))
            
            return block
    # =================== Ledger oprations ==============
    def check_ledger_integrity(self):
        blocks = [int(str(b.stem)) for b in self.ledger_dir.iterdir() if b.stem!="README"]
        if len(blocks)==0:
            return 0 # block 0 has an issue
        else:
            for block in blocks:
                blk = self.loadBlock(block)
                #Now verify the block content
                # TODO : check the block
                # if any arror retun the current block number
                return block
            return None # No blocks have problems

    def loadBlock(self, block_id):
        return pickle.load(open(self.ledger_dir/str(block_id),"rb"))

    def gossip_getCurrentLedger_infos(self, connection):
        """Request current ledger informations (last bloc id)
        """
        try:
            connection.send(
                    pickle.dumps(
                    GossipFrame(
                        BCN_GossipEvents.GET_LEDGER_INFOS,
                        ""
                    )
                    )
                )        
            return True
        except Exception as ex:
            self.log_exception(ex)
            return False
    # ================= Ledger queries ======================================
    def show_ledger(self):
        """Show the ledger content(may be too mush if used on very big networks with millions of transactions)
        """
        print(self.ledger)

    # ================= Block chain transactions management ====================    
    def push_transaction(self, inputs, outputs):
        """A transaction received from some node
        process it and return a validation or not
        Parameters
        ----------
        inputs  (dict) : A list of inputs (public key, amout, signature) pairs for input coins
        outputs (dict) : A list of outputs (public key, amout) pairs for output coins
        """
        # check that the sender_public_key has something in its wallet
        sender_money = 0
        for entry in self.ledger:
            if entry["receiver_public_key"]==sender_public_key:
                sender_money += entry["amount"]
            if entry["sender_public_key"]==sender_public_key:
                sender_money -= entry["amount"]
        # Now we know how much the sender_public_key have. let's check if he can actually send the money to the receiver_public_key
        if sender_money<amount:
            return False # Refuse transaction
        else:# Transaction is ok let's validate it
            # the sender_public_key cyphers this code using his private key, and put it in sender_val parameter
            #to verify this we use his public key. if we can decode 
            digest = hashes.Hash(hashes.SHA256())
            digest.update(bytes(str(ts)+str(sender_public_key)+str(receiver_public_key)+str(amount)))
            validation_code= digest.finalize()

            # Verify that the sender_public_key is the right sender_public_key
            try:
                sender_public_key.verify(
                    validation_code,
                    sender_val
                    )
                print('valid!')
            except InvalidSignature:
                print('invalid!')
                return False

            pending_entry = {
                "timestamp":ts,
                "sender_public_key":sender_public_key,# A dump root sender_public_key that is used just to create the stuff
                "sender_validation":sender_val, # the sender must sign the amount of money he wants to send using his private key 
                "receiver_public_key":receiver_public_key,
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
            hash_ = hash(bytes(str(ts)+str(pending_transaction["sender_public_key"])+str(pending_transaction["receiver_public_key"])+str(pending_transaction["amount"])))
            # Build ledger entry
            entry = {
                    "timestamp":pending_transaction["ts"],
                    "sender_public_key":pending_transaction["sender_public_key"],# A dump root sender_public_key that is used just to create the stuff
                    "receiver_public_key":pending_transaction["receiver_public_key"],
                    "amount":pending_transaction["amount"], # The maximum amount of coins for this blockchain
                    "Hash":hash_,
                    "Validation":sign(self.miner_private_key, hash_)
                }
            # Add it to the ledger
            self.ledger.append(entry)

    # ========================================================        
    # Logging
    # ========================================================        
    def log_exception(self, ex):
        """Logs an exception
        """
        type_, value_, traceback_ = sys.exc_info()
        print("[Exception]  {}\n{}\n{}\n{}\n".format(ex,type_,value_,'\n'.join(traceback.format_tb(traceback_))))
