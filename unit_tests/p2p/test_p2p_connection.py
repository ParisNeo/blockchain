# Unit test :
# Author : ParisNeo
# Description : Builds an instance of GossipNode that opens communication port on local and connect to virtually known nodes
from blockchain.p2p import GossipNode
import argparse
from blockchain.crypto_tools import generateKeys

parser = argparse.ArgumentParser()
parser.add_argument('-n', "--name", default="Miner0")
parser.add_argument('-a', "--addr", default="127.0.0.1")
parser.add_argument('-p', "--port", default=44444,type=int)
args = parser.parse_args()

private_key, public_key = generateKeys()

# Test GossipNode object creation with raw data (no miner key given and no )
bc = GossipNode(
                        private_key,
                        public_key,
                        
                        args.name,
                        args.addr,
                        args.port
                    )
# Start loop
bc.loop()