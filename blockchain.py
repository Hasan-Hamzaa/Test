# blockchain.py
import hashlib
import time
import json
import sqlite3
from p2pnetwork.node import Node
import socket
import random
import requests


class Blockchain:
    def __init__(self, difficulty=4, port=5001, address="127.0.0.1"):
        self.chain = []
        self.transactions = []
        self.difficulty = difficulty
        self.port = port + random.randint(1, 1000)  # Randomize port to avoid conflicts
        self.address = address

        # Change the port mapping
        port_to_flask = {
            5001: 8000,
            5002: 8001,
            5003: 8002,
            5004: 8003,
            5005: 8004
        }
        self.flask_port = port_to_flask.get(port, 8000)

        # Add these lines for peer tracking
        self.peer_ports = [8000, 8001, 8002, 8003, 8004]  # List of possible peer ports
        self.last_seen = {}  # Track last time peer was seen

        # Initialize node with required parameters
        self.node = Node(host=self.address,
                         port=self.port,
                         callback=self.my_callback)

        self.connected_peers = set()
        self.init_db()
        self.load_chain_from_db()
        self.node.start()

        # Connect to existing node if this is not the first node
        if self.flask_port != 8000:
            self.connect_to_network()

    def my_callback(self, event):
        if hasattr(event, 'id'):
            print(f"Peer connected: {event.id}")
            self.connected_peers.add(event.id)
            self.sync_chains(event)

    def connect_to_network(self):
        """Connect to existing node in the network"""
        try:
            # Try to connect to the first node (port 8000)
            response = requests.post(f'http://127.0.0.1:8000/register_node',
                                     json={'address': f'http://127.0.0.1:{self.flask_port}',
                                           'p2p_port': self.port})
            if response.status_code == 201:
                print(f"Successfully connected to network via port 8000")
                # Trigger chain sync
                self.sync_with_network()
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to network: {e}")

    def sync_with_network(self):
        """Sync chain with existing network"""
        try:
            response = requests.get(f'http://127.0.0.1:8000/get_chain')
            if response.status_code == 200:
                chain_data = response.json()
                if len(chain_data['chain']) > len(self.chain):
                    if self.is_chain_valid(chain_data['chain']):
                        self.chain = chain_data['chain']
                        self.persist_chain_to_db()
                        print("Chain synchronized with network")
        except requests.exceptions.RequestException as e:
            print(f"Failed to sync chain: {e}")

    def broadcast_transaction(self, transaction):
        """Broadcast transaction to all known peers"""
        # P2P network broadcast
        if hasattr(self.node, 'nodes'):
            for node in self.node.nodes:
                self.node.send_to_node(node, {"type": "NEW_TRANSACTION", "transaction": transaction})

        # HTTP broadcast to known peers
        for port in self.peer_ports:
            if port != self.flask_port:
                try:
                    url = f'http://127.0.0.1:{port}/receive_transaction'
                    requests.post(url, json={"transaction": transaction})
                except requests.exceptions.RequestException as e:
                    print(f"Failed to broadcast to peer {port}: {e}")

    def receive_transaction(self, transaction):
        """Handle receiving transaction from other nodes"""
        if self.is_valid_transaction(transaction):
            self.transactions.append(transaction)
            return True
        return False

    def is_valid_transaction(self, transaction):
        """Validate incoming transaction"""
        required_fields = ['sender', 'product', 'amount', 'type']
        return all(field in transaction for field in required_fields)

    def create_block(self, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.transactions,
            'previous_hash': previous_hash,
            'nonce': 0,
            'hash': None
        }
        block['hash'] = self.proof_of_work(block)
        self.transactions = []
        self.chain.append(block)
        self.store_block_in_db(block)
        return block

    def proof_of_work(self, block):
        while True:
            block_string = json.dumps(block, sort_keys=True).encode()
            hashed_string = hashlib.sha256(block_string).hexdigest()
            if hashed_string.startswith('0' * self.difficulty):
                return hashed_string
            block['nonce'] += 1

    def calculate_hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_transaction(self, sender, receiver, product, amount, transaction_type):
        transaction = {
            'sender': sender,
            'receiver': receiver,
            'product': product,
            'amount': amount,
            'type': transaction_type,
            'timestamp': time.time()
        }

        # Store in current node's database
        self.store_transaction_in_db(sender, receiver, product, amount, transaction_type)

        # Store in all other nodes' databases
        for port in self.peer_ports:
            if port != self.flask_port:
                other_db = f'database_{port}.db'
                try:
                    conn = sqlite3.connect(other_db)
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO transactions (sender, receiver, product, amount, type) VALUES (?, ?, ?, ?, ?)",
                        (sender, receiver, product, amount, transaction_type)
                    )
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"Error storing transaction in database {port}: {e}")
                finally:
                    if 'conn' in locals():
                        conn.close()

        # Add to pending transactions
        self.transactions.append(transaction)

        # Create block immediately (auto-mining)
        if self.get_latest_block() is None:
            previous_hash = '0'
        else:
            previous_hash = self.get_latest_block()['hash']

        self.create_block(previous_hash)

        # Try to broadcast to other nodes
        for port in self.peer_ports:
            if port != self.flask_port:
                try:
                    requests.post(f'http://127.0.0.1:{port}/receive_transaction',
                                  json={'transaction': transaction})
                except requests.exceptions.RequestException as e:
                    print(f"Failed to broadcast to node {port}: {e}")

        return len(self.chain)

    def check_peer_status(self):
        status = {}
        for port in self.peer_ports:
            if port != self.flask_port:  # Don't check self
                try:
                    response = requests.get(f'http://127.0.0.1:{port}/ping', timeout=1)
                    if response.status_code == 200:
                        status[port] = 'online'
                        self.last_seen[port] = time.time()
                    else:
                        status[port] = 'offline'
                except:
                    status[port] = 'offline'
        return status

    def get_latest_block(self):
        return self.chain[-1] if self.chain else None

    def is_chain_valid(self, chain):
        if not chain:
            return False

        if len(chain) == 1:
            return chain[0]['previous_hash'] == '0'

        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]

            block_data = {
                'index': current_block['index'],
                'timestamp': current_block['timestamp'],
                'transactions': current_block['transactions'],
                'previous_hash': current_block['previous_hash'],
                'nonce': current_block['nonce']
            }

            if current_block['previous_hash'] != previous_block['hash']:
                print(f"Invalid link between blocks {i - 1} and {i}")
                return False

            block_string = json.dumps(block_data, sort_keys=True).encode()
            if not hashlib.sha256(block_string).hexdigest().startswith('0' * self.difficulty):
                print(f"Invalid proof of work for block {i}")
                return False

        return True

    def sync_chains(self, node):
        self.node.send_to_node(node, {"type": "GET_CHAIN"})

    def handle_get_chain(self, peer):
        self.node.send_to_node(peer, {"type": "CHAIN", "chain": self.chain})

    def handle_chain(self, peer, chain_data):
        received_chain = chain_data['chain']
        if len(received_chain) > len(self.chain) and self.is_chain_valid(received_chain):
            print("Updating chain from peer")
            self.chain = received_chain
            self.persist_chain_to_db()
        else:
            print("Received chain is invalid")

    def init_db(self):
        db_name = f'database_{self.flask_port}.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blocks (
                    idx INTEGER PRIMARY KEY,
                    timestamp REAL,
                    transactions TEXT,
                    previous_hash TEXT,
                    nonce INTEGER,
                    hash TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT,
                    receiver TEXT,
                    product TEXT,
                    amount INTEGER,
                    type TEXT
                )
            """)
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
        finally:
            conn.close()

    def load_chain_from_db(self):
        db_name = f'database_{self.flask_port}.db'
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blocks ORDER BY idx")
            blocks = cursor.fetchall()

            if blocks:
                self.chain = []
                for block_data in blocks:
                    block = self.create_block_from_tuple(block_data)
                    self.chain.append(block)
            else:
                self.create_genesis_block()
        except sqlite3.Error as e:
            print(f"Error loading chain from database: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def create_genesis_block(self):
        genesis_block = self.create_block(previous_hash='0')
        print("Genesis Block Created:", genesis_block)

    def store_block_in_db(self, block):
        db_name = f'database_{self.flask_port}.db'
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO blocks (idx, timestamp, transactions, previous_hash, nonce, hash) VALUES (?, ?, ?, ?, ?, ?)",
                (block['index'], block['timestamp'], json.dumps(block['transactions']),
                 block['previous_hash'], block['nonce'], block['hash'])
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error storing block: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()

    def store_transaction_in_db(self, sender, receiver, product, amount, transaction_type):
        db_name = f'database_{self.flask_port}.db'
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO transactions (sender, receiver, product, amount, type) VALUES (?, ?, ?, ?, ?)",
                (sender, receiver, product, amount, transaction_type)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error storing transaction: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()

    def create_block_from_tuple(self, block_data):
        return {
            'index': block_data[0],
            'timestamp': block_data[1],
            'transactions': json.loads(block_data[2]),
            'previous_hash': block_data[3],
            'nonce': block_data[4],
            'hash': block_data[5]
        }

    def persist_chain_to_db(self):
        db_name = f'database_{self.flask_port}.db'
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM blocks")
            for block in self.chain:
                cursor.execute(
                    "INSERT INTO blocks (idx, timestamp, transactions, previous_hash, nonce, hash) VALUES (?, ?, ?, ?, ?, ?)",
                    (block['index'], block['timestamp'], json.dumps(block['transactions']),
                     block['previous_hash'], block['nonce'], block['hash'])
                )
            conn.commit()
            print("Blockchain persisted to database successfully.")
        except sqlite3.Error as e:
            print(f"Error persisting chain: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()