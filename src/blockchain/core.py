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
import string 
import ntplib 
import traceback, sys
import base64

# Useful classes ======================================
class GossipEvents_():
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

GossipEvents = GossipEvents_()

class ConnectionRole_():
    """List of connection roles in the network
    """
    def __init__(self):
        """List of acceptable events for gossip network
        """
        self._ConnectionRole={
            "MASTER":0,
            "CLIENT":1
        }

    def __getitem__(self, key):
        """A function to access the configuration using obj["key"]
        """
        return self._ConnectionRole[key]

    def __getattr__(self, key):
        """A function to access the settings directly using obj.key
        """
        return self._ConnectionRole[key]

ConnectionRole = ConnectionRole_()

class BlockChainNode(object):
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
        # We first need to be well synced
        try:
            self.time_keeper = ntplib.NTPClient()
            self.time = self.time_keeper.request(ntp_server_address, version=3)
            if self.time.offset>10:
                print("[TIME error] : Your PC is not syced enough with ntp servers. Please sync your clock")
            print(f"Time offset : {self.time.offset}")
        except Exception as ex:
            print(f"Couldn't contact time server")

        # Not ready yet to interact with the system until I am synced
        self.ready = False

        # List of blocks to request from the peer
        self.blocks_to_request=[]
        
        # Save keys in memory
        self.server_nick_name = server_nick_name
        self.server_address = server_address
        self.server_port = server_port

        self.miner_private_key = miner_private_key
        self.miner_public_key = miner_public_key


        self.mining_coinbase_retribution = mining_coinbase_retribution
        self.mining_transaction_fee = mining_transaction_fee
        self.mining_cap = mining_cap

        # prepare an identity block to be sent to who ever connects to us
        # Build my identity block
        peer_validation_message = "__BlockChainPeerValidationMessage__"+self.server_nick_name+self.server_address+str(self.server_port)
        signature = self.sign(miner_private_key,bytes(peer_validation_message, "utf8"))
        signature = base64.b64encode(signature).decode("utf8")
        self.identity = {
            "name" : self.server_nick_name,
            "addr":self.server_address,
            "port":self.server_port,
            "public_key":self.publicKey2Text(miner_public_key),
            "signature":signature #list(signature)
        }

        # Save ledger and pending transaction files
        self.ledger_dir = Path(ledger_dir)
        self.pending_transactions_file_name = Path(pending_transactions_file_name)


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
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((server_address, server_port))        # Bind to the port
        # Attempt connection to all known nodes
        for node in self.known_nodes:
            if not(node["addr"]==self.server_address and node["port"]==self.server_port):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect((node["addr"], node["port"]))
                    node["socket"]=s
                    self.connected_peers.append({"socket":s, "addr":node["addr"], "port":node["port"]})
                    start_new_thread(self.communication, (s,(node["addr"], node["port"]),ConnectionRole.CLIENT))
                    

                    print(f"[Main thread] Connected to node {(node['addr'], node['port'])}")
                except Exception as ex:
                    print(f"[Main thread] Node  {(node['addr'], node['port'])} unreachable")
                    self.log_exception(f"[Exception] {ex}")

        # If the pending transaction file exists, then load it
        if self.pending_transactions_file_name.exists():
            self.pending_transactions = pickle.load(open(str(self.pending_transactions_file_name),"rb"))
        else:
            self.pending_transactions = []

        # Start server
        start_new_thread(self.listen,())
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

    def build_new_legder(self):
            # Consider this miner as the root of the ledger. Build the new network
            net_id = random.randint(0,2000000000)
            txt_sender_key = self.publicKey2Text(self.miner_public_key)
            txt_receiver_key = self.publicKey2Text(self.miner_public_key)
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
                            "dest":self.publicKey2Text(self.miner_public_key)
                        }
            data = bytes(str(ts)+str(coinbase)+str(self.pending_transactions)+prev,"utf8")
            hash = self.hash(data)
            # Build ledger entry
            block = {
                    "blockID":id,
                    "timestamp":ts,
                    "Coinbase":coinbase,
                    "Transactions":self.pending_transactions,
                    "prev":prev,
                    "hash":hash,
                    "Validation":self.sign(self.miner_private_key, data).decode('latin-1')
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

    def generate_salt(self, size=10):
        """Generates a random sequence
        Parameters
        ----------
        size (int) : size of the sequence
        """
        # call random.choices() string module to find the string in Uppercase + numeric data.  
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = size))    
        print("The randomly generated string is : " + str(ran)) # print the random data  
        return ran

    # ======================= Federated P2P Communication code =========================== 
    def communication(self, c, full_addr, role):
        """TCP connection with the peer to talk to
        """
        try:
            # Say hello
            self.gossip_hello(c)
            #If I am a client, then ask for ledger information
            if role==ConnectionRole.CLIENT:
                self.gossip_getCurrentLedger_infos(c)
            # Now get to work
            while True:
                data = c.recv(4096*1000).decode("utf8")
                data_len = len(data)
                print(f"Received {data_len} bytes")
                if data_len>0:
                    data = json.loads(data)
                    data["infected_nodes"].append(self.identity["public_key"]) # Add me to the list of those who knows about this node
                    self.gossip_list.append(data)

                    # Parse received data
                    if data["type"]==GossipEvents.HELLO: # Hello message received
                        index = self.get_peer_index(full_addr[0], full_addr[1])
                        infos = self.connected_peers[index]
                        if not "private_key" in infos.keys(): # this is a new person we don't know his private key yet, so let's say hello
                            # Someone said hello, let's start by verifying that he is a legitimate user. Remember, this is a trustless system
                            if self.verifyPeerInfos(data['metadata']):
                                print(f"[com {full_addr}] Adding peer \n{data['metadata']['public_key']}")
                                # Contaminate all nodes in the network
                                for peer in self.connected_peers:
                                    if peer["socket"]!=c:
                                        peer["socket"].send(
                                            json.dumps(
                                            self.buildGossipFrame(
                                                GossipEvents.HELLO,
                                                data["metadata"]
                                            )
                                            ).encode("utf8")
                                        )
                                data["metadata"]["socket"]=c
                                self.connected_peers[index] = data["metadata"]
                            else:# bad peer!!
                                print(f"[Peer {full_addr} is bad!!] Refusing peer {full_addr}")
                                self.close_connection(c)
                                return
                    elif data["type"]==GossipEvents.GET_LEDGER_INFOS:
                        print(f"[Gossip packet] Received legder infos request from {full_addr}")
                        blocks_list = sorted([int(str(b.stem)) for b in self.ledger_dir.iterdir() if str(b.stem).isnumeric()])
                        c.send(
                                json.dumps(
                                self.buildGossipFrame(
                                    GossipEvents.LEDGER_INFOS,
                                    blocks_list[-1]
                                )
                                ).encode("utf8")
                            )
                            
                        print(f"[Gossip packet] Sent ledger ingfos to {full_addr}")
                    elif data["type"]==GossipEvents.LEDGER_INFOS:
                        print(f"Ledger infos {data['metadata']}")
                        blocks_list = [int(str(b.stem)) for b in self.ledger_dir.iterdir() if str(b.stem).isnumeric()]
                        local_ledger_blocks = sorted(blocks_list)
                        remote_ledger_last_block = data['metadata']
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
                            c.send(
                                    json.dumps(
                                    self.buildGossipFrame(
                                        GossipEvents.GET_LEDGER_BLOCK,
                                        self.blocks_to_request[0]
                                    )
                                    ).encode("utf8")
                                )
                        else:
                            print(f"[Notification] Ready to process")
                            self.ready=True
                        # Find the tip of the ledger and ask for all new blocks
                    elif data["type"]==GossipEvents.LEDGER_INFOS:
                        # Tofdo ,send the requested ledger block
                        pass
                        

        except Exception as ex:
            print(f"[com {full_addr}] Connection lost")
            self.log_exception(f"{ex}")
            self.close_connection(c)
            time.sleep(1)

    def close_connection(self, socket):
        socket.close()
        found=None
        for i,peer in enumerate(self.connected_peers):
            if peer["socket"]==socket:
                found=i
                break
        if found is not None:
            print("Peer removed from list")
            del self.connected_peers[found]     

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
    
            print(f'Connected to :{addr[0]}:{addr[1]}')
            self.connected_peers.append({"socket":c, "addr":addr[0], "port":addr[1]})
            # Start a new thread and return its identifier
            start_new_thread(self.communication, (c,addr,ConnectionRole.MASTER))
    
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
    def gossip_getCurrentLedger_infos(self, connection):
        """Request current ledger informations (last bloc id)
        """
        try:
            connection.send(
                    json.dumps(
                    self.buildGossipFrame(
                        GossipEvents.GET_LEDGER_INFOS,
                        ""
                    )
                    ).encode("utf8")
                )        
            return True
        except Exception as ex:
            self.log_exception(ex)
            return False

    def gossip_peer_is_connected(self, peer_infos):
        self.buildGossipFrame(
            GossipEvents.PEER_ON,
            peer_infos
        )
    # ================= Keys management ==================================
    def storeKeys(self, private_key, privk_file_path, pubk_file_path, pass_phrase=None):
        """Stores key to file with or without encryption
        Parameters
        ----------
        private_key (RSAPublicKey)  : The key to store


        """
        if pass_phrase is None: # No password (not recommended)
            pem_private = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        else:
            pem_private = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.BestAvailableEncryption(bytes(pass_phrase,"utf8"))
            )
        # Public key is public, so no need to encrypt it
        pem_public = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(privk_file_path,"wb") as f:
            f.write(pem_private)
        with open(pubk_file_path,"wb") as f:
            f.write(pem_public)
    
    def loadKeys(self, privk_file_path, pubk_file_path, pass_phrase=None):
        """Load a previously stored key pairs
        """
        if pass_phrase is None: # No password (not recommended)
            with open(privk_file_path, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                                key_file.read(),
                                password=None
                            )
        else:
            with open(privk_file_path, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                                key_file.read(),
                                password=bytes(pass_phrase,"utf8")
                            )
        with open(pubk_file_path, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                            key_file.read()
                        )
        return private_key, public_key

    def privateKey2Text(self, key):
        """Converts a private key to text
        """
        return "".join(key.private_bytes(
                                    encoding=serialization.Encoding.PEM,
                                    format=serialization.PrivateFormat.PKCS8,
                                    encryption_algorithm=serialization.NoEncryption()
                                ).decode("utf8")[len("-----BEGIN PRIVATE KEY-----")+1:-len("-----END PRIVATE KEY-----")-2].split("\n"))

    def publicKey2Text(self, key):
        """Converts a public key to text
        """
        return "".join(key.public_bytes(
                                    encoding=serialization.Encoding.PEM,
                                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                                ).decode("utf8")[len("-----BEGIN PUBLIC KEY-----")+1:-len("-----END PUBLIC KEY-----")-2].split("\n"))


    def text2PrivateKey(self, text):
        """Convert a text to a private key
        """
        return serialization.load_pem_private_key(bytes("-----BEGIN PRIVATE KEY-----\n"+text+"\n-----END PRIVATE KEY-----","utf8"))

    def text2PublicKey(self, text):
        """Convert a text to a key
        """
        txt_bytes = bytes("-----BEGIN PUBLIC KEY-----\n"+text+"\n-----END PUBLIC KEY-----","utf8")
        return serialization.load_pem_public_key(txt_bytes)


    # ================= cryptography helpers ======================================
    def hash(self, data):
        """Hash some data
        """
        # Hash the stuff we need to hash
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data)
        hash= digest.finalize()
        return hash

    def sign(self, private_key, message):
        """Sign a message
        Parameters
        ----------
        private_key (RSAPublicKey)   : The private key to sign the message with
        message     (str)            : The message to be signed
        """
        return private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )      

    def verify(self, public_key, message, signature):
        """Verify the message signature
        Parameters
        ----------
        public_key (RSAPublicKey)   : The public key to verify that the sender is the right one 
        message    (str)            : The signed message (used for verification)
        signature  (str)            : The signature
        """
        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )  
            return True
        except InvalidSignature as inv_signature:
            return False
    
    # ================= peers infos ======================================
    def get_peer_index(self, addr, port):
        """
        """
        for i,entry in enumerate(self.connected_peers):
            if entry["addr"]==addr and entry["port"]==port:
                return i
        return -1

    def verifyPeerInfos(self, metadata):
        """ Ferify that the peer is not a fraudulent one
        """
        public_key = self.text2PublicKey(metadata["public_key"])
        peer_validation_message = bytes("__BlockChainPeerValidationMessage__"+metadata["name"]+metadata["addr"]+str(metadata["port"]),"utf8")
        return self.verify(public_key, peer_validation_message, base64.b64decode(metadata["signature"]))

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

    # ========================================================        
    # Logging
    # ========================================================        
    def log_exception(self, ex):
        """Logs an exception
        """
        type_, value_, traceback_ = sys.exc_info()
        print("[Exception]  {}\n{}\n{}\n{}\n".format(ex,type_,value_,'\n'.join(traceback.format_tb(traceback_))))
