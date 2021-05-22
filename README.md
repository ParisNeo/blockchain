# Warning !!!
As for today, this project is still in its early stage and not yet ready to be used as final stable product to build your own blockchain based network. Any one who wants to participate is welcomed (more on contribution rules later in this README).

# Motivation
This year (by the end of 2020), I wanted to build a new PC. I bought everything except the GPU. I wanted to buy the nvidea RTX3070, but the prices gone wild and I ended up not buying any GPU and stuck with my old GT 620. I'm still waiting for the  price to drop. When I investigated this shortage, it turns out that it is mainly caused by mining. The huge hype about cryptocurrencies led to a shortage of GPUs. After long investigation, and discussion with some friends, I ended up realizing the huge impact cryptocurrency has on our global warming problem. I stumbled on this website from cambridge university https://cbeci.org/ that tracks estimated crypto consumption in real time. As of toway it is 118TWh/year. Which translates to around 0.5% of the world energetic consumption.

That's madness!!


In the same time, cryptocurrency is a very interesting concept that has its benefits as an alternative globalized financial system that promisses many applications merging the real and virtual world. More freedom, more transparency...

Unfortunately, it also comes with its problems including greedy speculation and market manipulation as it is very sensitive to news and tweets from important people. Which makes it in some sens a tool of control rather than a tool of freedom. We have seen those **shitcoins** as Vitalik Buterin call them being used to scam people promising high gains and making crypto trading some kind of gambling game.


So I decided to build a blockchain to explore all those concepts and try to provide an ecofriendly blockchain based network. This project is open for contributions. I do it in my spare time. All you need to know is basic undestanding of cryptography and the blockchain as well as python programing language and the main idea behind my proofing system. Fork it, code, then send a pull request.

# blockchain
A python API to build your own blockchain for your application.

# Why ?
Python is a very popular language. It is very friendly and easy to learn and understand. It contains very powerful concepts that makes it a 21st century programming language. 

Python is a cross platform interpreted language very suited for opensource applications and for sharing knowledge between developers. The code is clear, very well indented and simple to read and understand (most of the time).

Python can be introduced to the web via the Flask library which makes it capable of deploying very powerful applications on multiple plateforms.

Blockchain technology is a very powerful technology that allows the creation and the exchange of digital assets on a decentralized peer to peer network. Blockchain applications can range from cryptocurrency to more elaborated real world or virtual assets property proof. It is a very robust and secure method to store contracts between peers.

Comboining the two worlds seems evident. So I started this personal project in order to share my understanding of this technology with other people who may want to elaborate on it and build useful tools.

# Some basic rules
Here I set up some basic moral rules to work with this library, build apon it, fork it, enhance it etc..

## Rule number 1

This block chain **must** respect the nature by one of four ways :
- Build new services that can be benefic for solving ecological problems.
- Provide a service in replacement of existing service but with a lower carbon footprint
- Compensate the harm that can be introduced by using the blockchain by donations to environment protection associations or any other form of positive impacts on real world nature. Or by adding tax fees for pollution... (Use your imagination...)
- The service added to the community should be worth the environmental harm that it can cause.

If your project enters in one of these categories, then you're good to go. No **shitcoins** are welcomed here.

The objective is to decrease the carbon footprint which is a serious problem that will ultimately face blockchain technology in the future as the power consumption raises while the ressources are declining. Better be ready for that day !!


## Rule number 2

This block chain should be used to build fair and respectful asset exchange ecosystem that should be shielded against greedy speculation and provide a real value for the users.
- Cryptocurrency is accepted, but should build a serious stable project, not just some scam (No **shitcoins** are welcomed here). 
- Game assets are acceptable, but should be caped in order to avoid that the price of some asset reaches astronomic values rendering it a dangerous speculation bubble or harming the network by exploding transactions load.
- Art assets are acceptable as the blockchain do not chainge the fact that it actually can reach high value over time so no capping is needed for art assets.  
- Other NFT used for a variety of applications are welcomed if they provide a serious advantage to the user, nature or humanity.
- Use your imagination for the good of all minkind (and maybe alians too...)

## Rule number 3

Keep it simple. The code tries its maximum to be as simple as possible while giving the possibility to developers to develop their own smart contracts using... guess what? python. Yes, no weird specific language to build smart contracts. Just use python for everything.


## Rule number 4

Users have to have access to a simplified description of the system. How things work? What are the risks and what are the gains?
This blockchain should be transparent and accessible to any one anywhere on or off this planet. (Aliens are welcomed too).

# Technpological choices

Blockchain technology history is very long. After Satoshi Nakamoto started bitcoin, multiple evolutions, bugfixes, hard and soft forks have been made. New cryptocurrencies have been created. After the introduction of the etherium by Vitalik Buterin, the blockchain usage grew exponentially with the introduction of the smart contracts and non fungible tokens.

## Mining proofing
To be complient with rule number 1, Proof Of Work is out of the question. It is a very power hungry mechanism.

For now, it is one of the most interesting ways to keep that form of completely decentralized and trustless system while preserving a high level of security.

This leaves us with several other choices:

### Proof of Stake (PoS)
The idea behind proof of stake is to make destroying the network very disadvantagious to the miners allowed to validate the trasnactions. This is done by allowing miners to validate blocks proportionally to the stake they have (the amount of money they have on their account). No one likes to loose money, so this garantees that no miner tries to break the network. And if he wants to do it, he has to own more than 50% of the available coins which would be hard for well established cryptocurrencies.

So, the miners should lock coins on stake (coins are temporarely not accessible by the miner to be used but can be unlocked if the miner wants to quit the mining network). The miner is chosen by an algorithm that takes into acount the amount at stake that the miners have. The more stake you put, the higher the chance that you get to be chosen. So here we invest money instead of investing energy.  

### Proof of Burn (PoB)
Idealized by Iain Stewart. The proof of burn is a way the miner prooves its engagement to the network by investing money instead of enery (just like proof of stake).If you want to qualify for mining, you have to burn some coins (generally fractions of coins). By doing this, you destroy your own money, and you get the chance to win even more. Once every miner puts his bid, a random selection is made, and the winner get to do the mining by validating the block and win the coinbase distributed money + the fees of the transactions of the block. So it may be worth it to burn an amount of money to gain all of this. In some sense, this is like proof of stake. The difference is that the money is flushed to the sinc and will never be regained afterwards. The miner sacrifices some of his own money to proove his commitement. This money disapears from the network creating an artificial rarification of the currency. In some case, this pumps up the fiat value of the cryptocurrencey.

Some people argue tha this is less ecofriendly than the PoS as it destroys coins that consumed some enery to be built in the first place. You can judge.

### Proof of Capacity (PoC)
Well, if you don't want to proove your committment by doing some complex work like in PoW, by putting some money on stake like PoS or even literally burning your coins like in PoB, you can try this one. Proof of Capacity is another technique, where you proove that your have the biggest drive space. The one having the biggest hard drive gets a higher chance to mine the next block. The algorithm generates plots. Large datasets that are stored on your PC. The more space you have, the more chance you have to be selected to mine the next block. You should buy multiple hard disks, bind them togather and you increase your chance. No this is not sponsored by WD :p. As of today only Burstcoin uses this technique. Still, if we don't use alot of energy, buying hard disks could create other forms of pollution (carbon, but also plastic, chimical ...). So we are not going to use this one.

### Proof-of-Elapsed Time (PoE)
Not even woth mentioning as it uses a third party node which is completely against the spirit of distributed computing. 

### Proof of Good-Will (PoG) <Our solutoin>

The proofing system we propose uses a combination of proof of stake and a contribution to good deeds. As proof of stake, the miners put some stake to proove they are worthy giving them the right to mine. They somehow buy the right to mine by putting some money apart. Unlike Proof of Stake, the money is not given back to the miner. The miner buyes a slot of time with an amount of money such that statistically, the expected gains outweighs the amount invested. Here, the validation does not require alot of energy so the real gains of the miner are higher than those of classical PoW based systems. Unlike Proof of Burn, the money is not distroyed. The money is reinjected into circulation via donations to valid good deed associations. Qualifies as good deed, any association that provides irrifutable proof that they operate for :
- Fighting climate change
- Fighting human and animal hunger
- Fighting deseases
- Helping improove children's condition in the world
- Helping enhance the overall human condition 

New associations can send a request through the network providing their wallet public key and providing a cryptographic proof of their identity. They must get at least 75% of voting from the live mining nodes. Only nodes allowed to mine can vote for the associations. The idea behind this is that most miners will only accept valid associations as they would like their money to go to rightful associations and not scammers.

This proofing system can be offloaded to very low consumption systems such as a raspberry pi or an equivalent embedded system that can run a linux distribution with a python interpreter. This means that you can consume as low as around 5W with lows down to 1W for IDLE periods. Very far from the 1KW of Gaming Rigs or even higher insane megawatts of mining farms. In fact the mining itself consists in verifying a block integrity and signing it then infecting the network with this block that gets sealed off to the block chain.

We gain:
- No need to do lot of computing
- No need to have huge mining farms, a raspberry pi suffice
- Give access to anyone to actually mine without need for huge mining power
- People don't need to buy multiple mining rigs.
- To have the right to mine you should pay more to increase the chances to be chosen
- We support good causes

### Network format
We decided to go with a herarchical distributed network. 

A herarchical network is a network with main nodes that communicate between themselves and have access to the ledger full copy and temporary peer nodes that can connect to the network. In our case, any peer is considered a node if it makes a full copy of the legder. Otherwize, he can only push transactions to the network to be mined. Every body can read the ledger and provide a web based interface to show any transaction. 


# Objective

- Build a blockchain with a new proofing system (a proof of stake like for lower energy foot print).
- Create mining and transaction tools.
- Test it and share it with people.


# Contribution
As of now, the project is in its baby steps and may even stop if I loose motivation. But it is opensource, so anyone can take it to the next level if he wants. All code is opensource and should stay that way. No direct cryptocrurrency or blockchain system can be directly made of this repository content. People should build a cryptocurrency project and use this git as a submodule in their project or simply install it from pip when I will publish it.

This project can stay as a hub between all these subprojects that can benefit from each other and enhance each other mutually.

This one should stay as an API and be referenced by any project that uses it. The source code of this API should be provided to end users or at least a link to this git project should be provided.

To code:
- Present your request in the issues.
- We discuss.
- You fork the project
- You code
- You do a pull request
- I verify
- I merge

All developers will have their name mentioned in a specific board.
You may code :
- Core developement
- Test developement
- Attacks and hacks to robustify the code
- Examples (simple prototype cryptos or smart contracts)
- Documentation

# Sponsorship
The project is free and made on free time. No sponsoring is requested. No donations are requested. Developers are not payed to build this code. It is a hobby project that help understand this technology and imaging a new ways to better utilize it. It is a challenging project that can potentially be good for our society.


# Changelog
- 19/05/2021 : Added first data modules for a big reorganization of the software
- 17/05/2021 : Added first handshake code
- 15/05/2021 : Upgraded blockchain concerpts. Proof of stake scheme chosen
- 15/05/2021 : First working Blockchain with basic functionalities
- 13/05/2021 : First code started. A basic blockchain code

# Disclaimer

The software is still under development and is not tested enough. Possible security flaws may arise and can be compromizing. Use it at your own risk. The first versions can be used for test purposes or to understand the concept but not ready yet for production environment.

