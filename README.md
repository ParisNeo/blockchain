# blockchain
A simple to use and understand blockchain working on a peer to peer network.
The objective is to provide a code simple enough to build your own blockchain network. 
The blockchain can be used to build custom blockchain networks to store assets and contracts in a federated herarchical structure.
The network is based on the proof of stake instead of proof of work.
The library is flexible allowing multiple schemes of retribution with the possibility to cap the coins number or not, to pay miners directly from coinbase or via transaction fees or both..

A herarchical blockchain is a blockchain with main nodes that communicate between themselves and have access to the ledger full copy and temporary peer nodes that can connect to the network and if they have enough stake (owned by buying the coins), they can mine some coins which allow them to make more while sustaining the network.

The idea behind proof of stake is to make destroying the network very disadvantagious to the miners allowed to validate the trasnactions. This is done by allowing miners to validate blocks proportionally to the stake they have (the amount of money they have on their account). No one likes to loose money, so this garantees that no miner tries to break the network. And if he wants to do it, he has to own more than 50% of the available coins which would be hard for well established cryptocurrencies.

## Why proof of stake?
Bitcoin uses proof of work. In this case, anyone can mine. Miners compete by trying to solve a complicated puzzle (finding a random sequence so that the hash has a certain form). Who ever wins, gets the mining fees. The difficulty is increased as the number of miners increase. At a certain point, miners started to use high end GPUs, FPGAs and all sorts of optimized computing processors to enhance their gains. The problem then is that today bitcoin mining is an ecological disaster. Miners should pay for high end equipment and for their electricity bill. Which renders mining not profitable in many cases and increases drastically the power consumption.


## How we do it in this library ?

There are multiple ways to use the proof of stake technique invented around 2013 and started being deployed around 2016 in some altcoins. Here we try to build a custom technique and allow contributors to build attacks against the network and report issues. The objective is to settle on a ecofriendly way of validating the blocks that is sufficiently resilient to malicious attacks.

Every time we need to validate a block, a "chosen one" is elected to validate the block.
The chosen one choice takes into consideration his balance. Miners with higher balance are more likely to be lected than Miners with low balance. Once the block is validated, it is sent to the network through gossip. Each node, should validate that the content is OK (no fraud is involved). If a fraud is detected, the network unvalidates the block, blocks the validator for a certain amount of time, then select another validator. Hence, anyone with high stakes has no interest to make frauds as he needs to attack more than 50% of the network, and the others will block him which results in a loss for the miner.

The final vote (validate or not) is made by a proportional voting technique. Voices are not equivalent. The richer you get, the bigger your voice is.



Examples of use can be found in examples folder.
Unit tests are used to 

# Objective

- Build a blockchain with a new proofing system (a proof of stake like for lower energy foot print).
- Create mining and transaction tools.
- Test it and share it with people.

# Changelog
- 19/05/2021 : Added first data modules for a big reorganization of the software
- 17/05/2021 : Added first handshake code
- 15/05/2021 : Upgraded blockchain concerpts. Proof of stake scheme chosen
- 15/05/2021 : First working Blockchain with basic functionalities
- 13/05/2021 : First code started. A basic blockchain code

# Disclaimer

The software is still under development and is not tested enough. Possible security flaws may arise and can be compromizing. use it at your own risk. The first versions can be used for test purposes or to understand the concept but not ready yet for production environment.

