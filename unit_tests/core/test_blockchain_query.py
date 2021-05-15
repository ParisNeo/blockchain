# Unit test :
# Author : ParisNeo
# Description : Builds an instance of BlockChainNone that opens communication port on local and connect to virtually known nodes.
#               Then, do some quaries to visualize the content of the blockchain 
from blockchain.core import BlockChainNode
import argparse
from cryptography.hazmat.primitives.asymmetric import rsa

parser = argparse.ArgumentParser()
parser.add_argument('-n', "--name", default="Miner0")
parser.add_argument('-a', "--addr", default="127.0.0.1")
parser.add_argument('-p', "--port", default=44444,type=int)
args = parser.parse_args()

private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
public_key = private_key.public_key()

# Test Blockchain object creation with raw data (no miner key given and no )
bc = BlockChainNode(
                        private_key,
                        public_key,
                        
                        args.name,
                        args.addr,
                        args.port
                    )
# Start loop
bc.show_ledger()