# Project       : BlockChain
# Script        : core.py
# Author        : ParisNeo
# Description   : The core code for the blockchain project

from pathlib import Path
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
import pickle
from datetime import datetime
import time
import socket
import json
from threading import Thread, Lock
from _thread import start_new_thread
import random
from enum import Enum

class GossipEvents_():
    """List of acceptable events for gossip network
    """
    def __init__(self):
        """List of acceptable events for gossip network
        """
        self._GossipEvents={
            "HELLO":0,
            "PEER_ON":1
        }

    def __getitem__(self, key):
        """A function to access the configuration using obj["key"]
        """
        return self._GossipEvents[key]

    def __getattr__(self, key):
        """A function to access the settings directly using obj.key
        """
        return self._GossipEvents[key]

GossipEvents = GossipEvents_()

class BlockChainNode(object):
    """ Main class
    Manages the local ledger, synchronizes it with the rest of the network, decides who can mine, receives transactions requests 
    """
    
    def __init__(
                    self, 
                    server_nick_name="Miner",
                    server_address="127.0.0.1",
                    server_port=44444,
                    miner_private_key=rsa.generate_private_key(public_exponent=65537, key_size=4096),
                    known_nodes_file_name="nodes.txt",
                    ledger_file_name="./ledger.pkl", 
                    pending_transactions_file_name="./pending.pkl", 
                    root_key_store_file="./root_key.rsa",
                    root_key_pass_phrase="password"
                ):

        """Initialises the blockchain object

        Parameters
        ----------
        server_nick_name        (str)               : Local server name
        server_address          (str)               : Local server address of the node
        server_port             (int)               : Local server port

        miner_private_key       (RSAPrivateKey)     : the miner private key object to sign and validate stuff

        known_nodes_file_name   (str or Path)       : a file containing nodes of the network to which we try to connect for the federated decentralyzed network
        ledger_file_name        (Path or str)       : the name of the file containing the ledger

        pending_transactions_file_name(Path or str) : A file to store the pending transactions in case of loss 
        root_key_store_file     (Path or str)       : A file to store the root key if this is the first of the first node (when you want to build a new network)
        root_key_pass_phrase    (Path or str)       : A passphrase to secure the file containing the root key pairs

        """

        # Save keys in memory
        self.server_nick_name = server_nick_name
        self.server_address = server_address
        self.server_port = server_port

        miner_private_key=rsa.generate_private_key(public_exponent=65537, key_size=512)
        self.miner_private_key = miner_private_key

        # prepare an identity block to be sent to who ever connects to us
        self.txt_public_key  = "".join(miner_private_key.public_key().public_bytes(
                                    encoding=serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                                ).decode("utf8")[len("-----BEGIN PUBLIC KEY-----")+1:-len("-----END PUBLIC KEY-----")-2].split("\n"))
        self.identity = {
            "name" : self.server_nick_name,
            "addr":self.server_address,
            "port":self.server_port,
            "public_key":self.txt_public_key,
        }

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
            with open(root_key_store_file,'w') as f:
                pem = private_key.private_bytes(
                                                encoding=serialization.Encoding.PEM,
                                                format=serialization.PrivateFormat.PKCS8,
                                                encryption_algorithm=serialization.BestAvailableEncryption(bytes(root_key_pass_phrase,"utf8"))
                                                )
                f.write(pem.decode("utf8"))

            #Build a ledger with a first virtual transaction to the root id
            ts = datetime.now().timestamp()

            # Hash the stuff we need to hash
            digest = hashes.Hash(hashes.SHA256())
            str_pc = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
            data = bytes(str(ts)+str_pc.decode("utf8")+str_pc.decode("utf8"),"utf8")
            digest.update(data)
            hash= digest.finalize()

            # Build ledger entry
            entry = {
                    "timestamp":ts,
                    "sender_public_key":0,# A dump root sender_public_key that is used just to create the stuff
                    "sender_validation":private_key.sign(
                                                            hash,
                                                            padding.PSS(
                                                                mgf=padding.MGF1(hashes.SHA256()),
                                                                salt_length=padding.PSS.MAX_LENGTH
                                                            ),
                                                            hashes.SHA256()
                                                        ),
                    "receiver_public_key":public_key.public_bytes(
                                                            encoding=serialization.Encoding.PEM,
                                                            format=serialization.PublicFormat.SubjectPublicKeyInfo
                                                        ),
                    "amount":100000000000, # The maximum amount of coins for this blockchain
                    "Hash":hash,
                    "Validation":private_key.sign(hash,
                                                        padding.PSS(
                                                            mgf=padding.MGF1(hashes.SHA256()),
                                                            salt_length=padding.PSS.MAX_LENGTH
                                                        ),
                                                        hashes.SHA256()
                                                    ),
                }
            self.ledger=[
                entry
            ]
            pickle.dump(self.ledger,open(str(self.ledger_file_name),"wb"))



        # ===========================
        # Communication
        # ===========================
        # Let's keep a list of connected peers
        self.connected_peers = []
        # Let's read the lost of known nodes in the network (needed bor the backbone of the federated decentralyzed network)
        self.known_nodes_file_name = Path(known_nodes_file_name)
        self.known_nodes = []
        if self.known_nodes_file_name.exists():
            with open(str(self.known_nodes_file_name),"r") as f:
                n_vals = f.read()
                nodes = n_vals.split("\n")
                for node in nodes:
                    try:
                        addr, port = node.split(":")
                        self.known_nodes.append({
                                                    "name":None,
                                                    "addr":addr,
                                                    "port":int(port),
                                                    "public_key":None,
                                                    "socket":None
                                                })                        
                    except:
                        pass
        # Gossip list a list of information to tell others about 
        self.gossip_list = []

        # Build a socket to listen to messages
        self.server = socket.socket()
        self.server.bind((server_address, server_port))        # Bind to the port
        self.print_lock = Lock()
        start_new_thread(self.listen,())
        # Attempt connection to all known nodes
        for node in self.known_nodes:
            if not(node["addr"]==self.server_address and node["port"]==self.server_port):
                s = socket.socket()
                try:
                    s.connect((node["addr"],node["port"]))
                    node["socket"]=s
                    start_new_thread(self.communication, (s,(node["addr"],node["port"])))
                    self.gossip_hello(s)
                    print(f"[Main thread] Connected to node {(node['addr'],node['port'])}")
                except:
                    print(f"[Main thread] Node  {(node['addr'],node['port'])} unreachable")

    # ======================= Federated P2P Communication code =========================== 
    def communication(self, c, addr):
        """TCP connection with the peer to talk to
        """
        try:
            while True:
                data = c.recv(4096*1000).decode("utf8")
                print(len(data))
                data = json.loads(data)
                data["infected_nodes"].append(self.identity["public_key"]) # Add me to the list of those who knows about this node
                self.gossip_list.append(data)
                if data["type"]==GossipEvents.HELLO:
                    self.connected_peers.append(data["metadata"])
        except Exception as ex:
            c.close()
            print(f"[com {addr}] error reading\n{ex}")
            time.sleep(1)


    def listen(self):
        """Listen to peer connections
        """
        print(f"[TH Lestining] Listening on address {self.server_address}:{self.server_port}")
        # put the socket into listening mode
        self.server.listen(5)
        print("socket is listening")
    
        # a forever loop until client wants to exit
        while True:    
            # establish connection with client
            c, addr = self.server.accept()
    
            # lock acquired by client
            self.print_lock.acquire()
            print(f'Connected to :{addr[0]}:{addr[1]}')
            # Start a new thread and return its identifier
            start_new_thread(self.communication, (c,addr))
            # Say hello
            self.gossip_hello(c)
    
        s.close()

    def loop(self):
        """Starts events loop
        """
        self.started = True
        while self.started:
            time.sleep(1)

    def pushGossipFrame(self, frame):
        """Pushes a gossip frame to pending frames list
        """
        self.gossip_list.append(frame)

    def buildGossipFrame(self, type, metadata):
        """Builds a gossip frame to inform other nodes of something
        """
        return {
                "message_id":random.randint(0,2000000000),
                "ts":datetime.now().timestamp(),
                "type":type,
                "metadata":metadata,
                "infected_nodes":[self.identity["public_key"]]
        }
        
    def gossip_hello(self, connection):
        connection.send(
            json.dumps(
            self.buildGossipFrame(
                GossipEvents.HELLO,
                self.identity
            )
            ).encode("utf8")
        )

    def gossip_peer_is_connected(self, peer_infos):
        self.buildGossipFrame(
            GossipEvents.PEER_ON,
            peer_infos
        )

    # ================= Block chain transactions management ====================    
    def push_transaction(self, data):
        """A transaction received from some node
        process it and return a validation or not
        """
        ts = data["ts"]
        sender_public_key = data["sender_public_key"]
        sender_val = data["sender_val"]
        receiver_public_key = data["receiver_public_key"]
        amount = data["amount"]


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
            digest = hashes.Hash(hashes.SHA256())
            digest.update(bytes(str(ts)+str(pending_transaction["sender_public_key"])+str(pending_transaction["receiver_public_key"])+str(pending_transaction["amount"])))
            hash= digest.finalize()
            # Build ledger entry
            entry = {
                    "timestamp":pending_transaction["ts"],
                    "sender_public_key":pending_transaction["sender_public_key"],# A dump root sender_public_key that is used just to create the stuff
                    "receiver_public_key":pending_transaction["receiver_public_key"],
                    "amount":pending_transaction["amount"], # The maximum amount of coins for this blockchain
                    "Hash":hash,
                    "Validation":self.miner_private_key.sign(hash)
                }
            # Add it to the ledger
            self.ledger.append(entry)
