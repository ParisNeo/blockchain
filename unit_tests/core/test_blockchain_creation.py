# Unit test :
# Author : ParisNeo
# Description : Builds an instance of BlockChainNone that opens communication port on local and connect to virtually known nodes
from blockchain.core import BlockChainNode
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-n', "--name", default="Miner0")
parser.add_argument('-a', "--addr", default="127.0.0.1")
parser.add_argument('-p', "--port", default=44444,type=int)
args = parser.parse_args()

# Test Blockchain object creation with raw data (no miner key given and no )
bc = BlockChainNode(args.name, args.addr, args.port)
# Start loop
bc.loop()