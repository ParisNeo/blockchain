# Unit test :
# Author : ParisNeo
# Description : Builds an instance of BlockChainNone that opens communication port on local and connect to virtually known nodes.
#               Then, test message signature and validation using private and public key pairs
from blockchain.core import BlockChainNode
from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
public_key = private_key.public_key()

# Test Blockchain object creation with raw data (no miner key given and no )
bc = BlockChainNode(
                        private_key,
                        public_key
                    )
print("Testing Private key conversion ")
print(bc.privateKey2Text(bc.miner_private_key))
print("Public key conversion ")
print(bc.publicKey2Text(bc.miner_private_key.public_key()))

print("")
print("Initial test ")
signature = bc.sign(bc.miner_private_key, b"Hello world")
verif = bc.verify(bc.miner_private_key.public_key(), b"Hello world", signature)
print(f"Verification : {verif}") # Should be true


print("========== Testing no password saving ============")
print("Save")
bc.storeKeys(bc.miner_private_key,"private.pem","public.pem")
#Let's load the keys and try the signature

print("Reload")
priv, pub = bc.loadKeys("private.pem","public.pem")

print("New test")
signature = bc.sign(priv, b"Hello world")
verif = bc.verify(pub, b"Hello world", signature)
print(f"Verification : {verif}") # Should be true

print("========== Testing with password saving ============")
print("Save")
bc.storeKeys(bc.miner_private_key,"private.pem","public.pem","test_pass_phrase")
#Let's load the keys and try the signature

print("Reload")
priv, pub = bc.loadKeys("private.pem","public.pem","test_pass_phrase")

print("New test")
signature = bc.sign(priv, b"Hello world")
verif = bc.verify(pub, b"Hello world", signature)
print(f"Verification : {verif}") # Should be true


