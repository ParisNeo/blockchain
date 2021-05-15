# Infos

This block chain saves the ledger as a list of pickle files. Each file is a block and blocks have block ids as file names.
Each block has the hash of the previous one  so that no malicious code could change the hash.
We also use signing using the miner private key in order to validate that he is the one who validated the block. The miner can't cheat as he will be slashed by other nodes if he does so. As they should verify the block before accepting it.

So technically, every miner verifies the transaction. If more than 50% of miners coin owners say this is a fraudulent transaction, the miner is slashed. Which means he looses the right to validate transactions for an amount of time.