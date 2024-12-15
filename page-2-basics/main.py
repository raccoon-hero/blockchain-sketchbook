import hashlib
import time
from flask import Flask, jsonify, request, render_template

class PKO_Transaction:
    def __init__(self, sender, receiver, amount, fee=0):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.fee = fee

    def __str__(self):
        return f'{self.sender} -> {self.receiver}: {self.amount} PKO, Commission Fee: {self.fee} PKO'

class PKO_Mempool:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)
        return f"Transaction added: {transaction}"

class PKO_MerkleTree:
    def __init__(self, transactions):
        self.transactions = transactions
        self.root = self.build_merkle_tree([self.hash_transaction(tx) for tx in transactions])

    def hash_transaction(self, transaction):
        transaction_string = str(transaction)
        return hashlib.sha256(transaction_string.encode('utf-8')).hexdigest()

    def build_merkle_tree(self, hashed_transactions):
        if len(hashed_transactions) == 1:
            return hashed_transactions[0]

        if len(hashed_transactions) % 2 != 0:
            hashed_transactions.append(hashed_transactions[-1])

        new_level = []
        for i in range(0, len(hashed_transactions), 2):
            combined_hash = self.hash_pair(hashed_transactions[i], hashed_transactions[i+1])
            new_level.append(combined_hash)

        return self.build_merkle_tree(new_level)

    def hash_pair(self, hash1, hash2):
        combined = hash1 + hash2
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

class PKO_Block:
    def __init__(self, index, previous_hash, merkle_root, difficulty):
        self.index = index
        self.previous_hash = previous_hash
        self.merkle_root = merkle_root
        self.timestamp = time.time()
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = self.mine_block()

    def calculate_hash(self):
        block_string = f'{self.index}{self.previous_hash}{self.merkle_root}{self.timestamp}{self.nonce}'
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()

    def mine_block(self):
        print(f"Mining block #{self.index}...")
        target = '0' * self.difficulty
        while True:
            self.hash = self.calculate_hash()
            if self.hash[:self.difficulty] == target:
                break
            self.nonce += 1
        print(f"Block Mined! Nonce: {self.nonce}, Hash: {self.hash}")
        return self.hash

class PKO_Blockchain:
    def __init__(self):
        self.chain = []
        self.mempool = PKO_Mempool()
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = PKO_Block(0, "0", "Genesis Block", difficulty=4)
        self.chain.append(genesis_block)

    def add_block(self, miner_address):
        total_fees = sum(tx.fee for tx in self.mempool.transactions)

        # COINBASE-TRANSACTION
        coinbase_transaction = PKO_Transaction("Network", miner_address, 1 + total_fees)
        self.mempool.transactions.insert(0, coinbase_transaction) 

        # NEW BLOCK CREATION
        previous_block = self.chain[-1]
        self.merkle_tree = PKO_MerkleTree(self.mempool.transactions)  
        new_block = PKO_Block(len(self.chain), previous_block.hash, self.merkle_tree.root, difficulty=4)

        all_transactions = [str(tx) for tx in self.mempool.transactions]

        self.chain.append(new_block)

        self.mempool.transactions = []  

        return new_block, all_transactions

    def get_chain(self):
        return [block.__dict__ for block in self.chain]


app = Flask(__name__)
blockchain = PKO_Blockchain()

# LANDING PAGE
@app.route('/')
def index():
    return render_template('index.html')

# NEW TRANSACTION
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    fee = values.get('fee', 0)

    transaction = PKO_Transaction(values['sender'], values['receiver'], values['amount'], fee)
    result = blockchain.mempool.add_transaction(transaction)
    return jsonify({'message': result}), 201

# MINE BLOCK
@app.route('/mine', methods=['POST'])
def mine():
    values = request.get_json()
    miner_address = values.get('miner')

    if miner_address is None:
        return 'Miner address is required', 400

    block, all_transactions = blockchain.add_block(miner_address)

    response = {
        'message': 'New block mined',
        'index': block.index,
        'transactions': all_transactions, 
        'previous_hash': block.previous_hash,
        'hash': block.hash,
        'nonce': block.nonce,
        'merkle_root': block.merkle_root
    }
    return jsonify(response), 200


# SEE BLOCKCHAIN
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.get_chain(),
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

# LAUNCH SERVER
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
