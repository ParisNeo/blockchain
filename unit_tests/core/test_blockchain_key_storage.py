# Unit test :
# Author : ParisNeo
# Description : Builds an instance of BlockChainNone that opens communication port on local and connect to virtually known nodes.
#               Then, test message signature and validation using private and public key pairs
from blockchain import BlockChainNode
from blockchain import BlockChainNode
import argparse
from blockchain.crypto_tools import generateKeys, privateKey2Text, text2PrivateKey, publicKey2Text, text2PublicKey, sign, verify

parser = argparse.ArgumentParser()
parser.add_argument('-n', "--name", default="Miner0")
parser.add_argument('-a', "--addr", default="127.0.0.1")
parser.add_argument('-p', "--port", default=44444,type=int)
args = parser.parse_args()

private_key, public_key = generateKeys()

# Test Blockchain object creation with raw data (no miner key given and no )
bc = BlockChainNode(
                        private_key,
                        public_key,

                        args.name,
                        args.addr,
                        args.port
                    )
print("Testing Private key conversion ")
print(privateKey2Text(bc.miner_private_key))
print("Public key conversion ")
print(publicKey2Text(bc.miner_private_key.public_key()))

print("")
print("Initial test ")
signature = sign(bc.miner_private_key, b"Hello world")
verif = verify(bc.miner_private_key.public_key(), b"Hello world", signature)
print(f"Verification : {verif}") # Should be true


print("========== Testing no password saving ============")
print("Save")
bc.storeKeys(bc.miner_private_key,"private.pem","public.pem")
#Let's load the keys and try the signature

print("Reload")
priv, pub = bc.loadKeys("private.pem","public.pem")

print("New test")
signature = sign(priv, b"Hello world")
verif = verify(pub, b"Hello world", signature)
print(f"Verification : {verif}") # Should be true

print("========== Testing with password saving ============")
print("Save")
bc.storeKeys(bc.miner_private_key,"private.pem","public.pem","test_pass_phrase")
#Let's load the keys and try the signature

print("Reload")
priv, pub = bc.loadKeys("private.pem","public.pem","test_pass_phrase")

print("New test")
signature = sign(priv, b"Hello world")
verif = verify(pub, b"Hello world", signature)
print(f"Verification : {verif}") # Should be true


