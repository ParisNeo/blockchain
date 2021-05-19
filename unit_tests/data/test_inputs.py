# Unit test :
# Author : ParisNeo
# Description : Tests building a simple input for a transaction and verifying it and testing it against malicious data change

from blockchain.data.input import Input
from blockchain.crypto_tools import generateKeys

private_key, public_key = generateKeys()

inp = Input(private_key, public_key, 100)
print(inp)
print("Valid" if inp.verify() else "Unvalid")

inp.amount+=1
print("Valid" if inp.verify() else "Unvalid")
