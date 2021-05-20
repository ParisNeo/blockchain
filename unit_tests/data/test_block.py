# Unit test :
# Author : ParisNeo
# Description : Tests building a simple input for a transaction, put it in a block, sign everything and test. Then intentionally add an error and retest
# Expected behaviour : First everything is valid. After altering the amount for the transaction, every thing is unvalid

from blockchain.data.transaction import Transaction
from blockchain.data.input import Input
from blockchain.data.output import Output
from blockchain.data.block import Block
from blockchain.crypto_tools import generateKeys
import time


sender_private_key, sender_public_key = generateKeys()
receiver_private_key, receiver_public_key = generateKeys()
miner_private_key, miner_public_key = generateKeys()

inp = Input(sender_private_key, sender_public_key, 100)

outp = Output(receiver_public_key, 100)



print(inp)
print(outp)


transaction = Transaction(0, time.time(),[inp],[outp])
transaction.sign(miner_private_key)
block = Block(0,coinbase=Transaction(0, time.time(),[],[Output(miner_public_key, 10)]),transactions=[transaction])
block.sign(miner_private_key)
print("Valid block" if block.verify(miner_public_key) else "Unvalid block")



# Show that if someone temper with the transaction, we will detect it
print("Valid input" if inp.verify() else "Unvalid Input")
# Let's save our block
block.save("./ledgers/ledger")
print("Valid transaction" if transaction.verify(miner_public_key) else "Unvalid transaction")



inp.amount+=1
print("Valid Input" if inp.verify() else "Unvalid Input")
print("Valid transaction" if transaction.verify(miner_public_key) else "Unvalid transaction")
print("Valid block" if block.verify(miner_public_key) else "Unvalid block")

# Now load the saved block
block.load("./ledgers/ledger",0)
# Retest validity of the block
print("Valid block" if block.verify(miner_public_key) else "Unvalid block")
