# Project       : BlockChain
# Script        : gossip_net.py
# Author        : ParisNeo
# Description   : A simplified version of gossip peer to peer network protocol


from datetime import datetime
from pathlib import Path
import time
import datetime
import sys, traceback
import socket
import json
import pickle
import ntplib 
from threading import Thread, Lock
from _thread import start_new_thread
import time
from blockchain.crypto_tools import b58decode, b58encode, sign, verify, publicKey2Text, text2PublicKey

import random
# Useful classes ======================================
class GossipEvents_():
    """List of acceptable events for gossip network
    """
    def __init__(self):
        """List of acceptable events for gossip network
        """
        self._GossipEvents={
            "HELLO":0
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


class PeerIdentity():
    def __init__(self, nick_name="", address="", port=0, public_key=None, signature=None, socket = None):
        self.nick_name  = nick_name
        self.address    = address
        self.port       = port
        self.public_key = public_key
        self.signature  = signature

        self.socket     = socket

    def __str__(self):
        return f"{self.nick_name} ({self.address}:{self.port})"


class GossipFrame():
    def __init__(self, type, metadata):
        """Builds a gossip frame to inform other nodes of something
        """
        self.message_id     = random.randint(0,2000000000)
        self.ts             = datetime.datetime.now().timestamp()
        self.type           = type
        self.metadata       = metadata


class GossipNode(object):
    """ Main class
    Builds a computational node that can nonnect to the p2p network and exchange data
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

      
        # Save keys in memory
        self.server_nick_name = server_nick_name
        self.server_address = server_address
        self.server_port = server_port

        self.miner_private_key = miner_private_key
        self.miner_public_key = miner_public_key

        # prepare an identity block to be sent to who ever connects to us
        # Build my identity block
        peer_validation_message = "__BlockChainPeerValidationMessage__"+self.server_nick_name+self.server_address+str(self.server_port)
        signature = sign(miner_private_key,bytes(peer_validation_message, "utf8"))
        self.identity=PeerIdentity(self.server_nick_name, self.server_address, self.server_port, publicKey2Text(miner_public_key), signature)
        # Save ledger and pending transaction files


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
                        self.known_nodes.append(PeerIdentity("",addr,int(port),None, None, None))                        
                    except:
                        pass
        # Gossip list a list of information to tell others about 
        self.gossip_list = []

        # Build a socket to listen to messages
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((server_address, server_port))        # Bind to the port
        # Attempt connection to all known nodes
        for node in self.known_nodes:
            if not(node.address==self.server_address and node.port==self.server_port):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect((node.address, node.port))
                    node.socket=s
                    self.connected_peers.append(node)
                    start_new_thread(self.communication, (node,ConnectionRole.CLIENT))
                    

                    print(f"[Main thread] Connected to node {(node.address, node.port)}")
                except Exception as ex:
                    print(f"[Main thread] Node  {(node.address, node.port)} unreachable")
                    self.log_exception(f"[Exception] {ex}")


        # Start server
        start_new_thread(self.listen,())


    def communication(self, node, role):
        """TCP connection with the peer to talk to
        """
        try:
            # Say hello
            self.gossip_hello(node.socket)
            #If I am a client, then ask for ledger information
            if role==ConnectionRole.CLIENT:
                self.gossip_getCurrentLedger_infos(node.socket)
            # Now get to work
            while True:
                data = pickle.loads(node.socket.recv(4096*1000))
                self.gossip_list.append(data)

                # Parse received data
                if data.type==GossipEvents.HELLO: # Hello message received
                    index = self.get_peer_index(node.address, node.port)
                    infos = self.connected_peers[index]
                    if infos.public_key is None: # this is a new person we don't know his public key yet, so let's say hello
                        # Someone said hello, let's start by verifying that he is a legitimate user. Remember, this is a trustless system
                        if self.verifyPeerInfos(data.metadata):
                            print(f"[com {node}] Adding peer \n{data.metadata.public_key}")
                            # Contaminate all nodes in the network
                            for peer in self.connected_peers:
                                if peer.socket!=node.socket:
                                    peer.socket.send(
                                        pickle.dumps(
                                        GossipFrame(
                                            GossipEvents.HELLO,
                                            data.metadata
                                        )
                                        )
                                    )
                            data.metadata.socket=node.socket
                            self.connected_peers[index] = data.metadata
                        else:# bad peer!!
                            print(f"[Peer {node} is bad!!] Refusing peer {node}")
                            self.close_connection(node.socket)
                            return
                else:
                    self.process(node, data)

        except Exception as ex:
            print(f"[com {node}] Connection lost")
            self.log_exception(f"{ex}")
            self.close_connection(node.socket)
            time.sleep(1)

    def process(self, node, data):
        """ Process to be done by the inheriting class
        """
        pass
                

    def close_connection(self, socket):
        socket.close()
        found=None
        for i,peer in enumerate(self.connected_peers):
            if peer.socket==socket:
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
            node = PeerIdentity()
            node.socket, (node.address, node.port) = self.server.accept()
    
            print(f'Connected to :{node}')
            self.connected_peers.append(node)
            # Start a new thread and return its identifier
            start_new_thread(self.communication, (node,ConnectionRole.MASTER))
    
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


        
    def gossip_hello(self, connection):
        connection.send(
            pickle.dumps(
            GossipFrame(
                GossipEvents.HELLO,
                self.identity
            )
            )
        )

    def gossip_peer_is_connected(self, peer_infos):
        GossipFrame(
            GossipEvents.PEER_ON,
            peer_infos
        )
    # ================= peers infos ======================================
    def get_peer_index(self, addr, port):
        """
        """
        for i,entry in enumerate(self.connected_peers):
            if entry.address==addr and entry.port==port:
                return i
        return -1

    def verifyPeerInfos(self, metadata: PeerIdentity):
        """ Ferify that the peer is not a fraudulent one
        """
        public_key = text2PublicKey(metadata.public_key)
        peer_validation_message = bytes("__BlockChainPeerValidationMessage__"+metadata.nick_name+metadata.address+str(metadata.port),"utf8")
        return verify(public_key, peer_validation_message, metadata.signature)

    # ========================================================        
    # Logging
    # ========================================================        
    def log_exception(self, ex):
        """Logs an exception
        """
        type_, value_, traceback_ = sys.exc_info()
        print("[Exception]  {}\n{}\n{}\n{}\n".format(ex,type_,value_,'\n'.join(traceback.format_tb(traceback_))))