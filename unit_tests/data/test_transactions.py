# Unit test :
# Author : ParisNeo
# Description : Tests building a simple input for a transaction and verifying it and testing it against malicious data change

from blockchain.data.transaction import Transaction
from blockchain.data.input import Input
from blockchain.data.output import Output
from blockchain.crypto_tools import generateKeys
import time
sender_private_key, sender_public_key = generateKeys()
receiver_private_key, receiver_public_key = generateKeys()
miner_private_key, miner_public_key = generateKeys()

inp = Input(sender_private_key, sender_public_key, 100)

outp = Output(receiver_public_key, 100)



print(inp)
print(outp)


transaction =Transaction(0, time.time(),[inp],[outp])
transaction.sign(miner_private_key)


# Show that if someone temper with the transaction, we will detect it
print("Valid input" if inp.verify() else "Unvalid Input")
print("Valid transaction" if transaction.verify(miner_public_key) else "Unvalid transaction")
inp.amount+=1
print("Valid Input" if inp.verify() else "Unvalid Input")
print("Valid transaction" if transaction.verify(miner_public_key) else "Unvalid transaction")
