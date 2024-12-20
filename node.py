# node.py
from flask import Flask, jsonify, request, render_template
from blockchain import Blockchain
import json
import argparse
import sqlite3
import requests

app = Flask(__name__)

# Command-line arguments for P2P port
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=5001, help="Port for the blockchain node")
args = parser.parse_args()

blockchain = Blockchain(difficulty=2, port=args.port)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sell')
def sell_page():
    return render_template('sell.html')

@app.route('/buy')
def buy_page():
    listings = []
    for block in blockchain.chain:
        for tx in block['transactions']:
            if tx['type'] == 'list':
                listings.append(tx)
    return render_template('buy.html', listings=listings)

@app.route('/receive_transaction', methods=['POST'])
def receive_transaction():
    """Endpoint to receive transactions from other nodes"""
    transaction_data = request.get_json()
    if blockchain.receive_transaction(transaction_data['transaction']):
        return jsonify({'message': 'Transaction received and accepted'}), 200
    return jsonify({'message': 'Invalid transaction'}), 400

@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_latest_block()
    if previous_block is None:
        previous_hash = '0'
    else:
        previous_hash = previous_block['hash']

    block = blockchain.create_block(previous_hash)
    response = {'message': 'Block mined successfully!', 'block': block}
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain, 'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'The blockchain is valid.'}
    else:
        response = {'message': 'The blockchain is not valid!'}
    return jsonify(response), 200

@app.route('/view_database', methods=['GET'])
def view_database():
    db_name = f'database_{blockchain.flask_port}.db'
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM blocks")
    blocks = cursor.fetchall()

    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()

    conn.close()

    formatted_blocks = []
    for block in blocks:
        formatted_blocks.append(blockchain.create_block_from_tuple(block))

    return jsonify({'blocks': formatted_blocks, 'transactions': transactions}), 200


# node.py (continued)
@app.route('/register_node', methods=['POST'])
def register_node():
    node_data = request.get_json()
    if not node_data:
        return "Error: Please supply valid node data", 400

    node_address = node_data.get('address')
    p2p_port = node_data.get('p2p_port')

    if node_address is None:
        return "Error: Please supply a valid node address", 400

    blockchain.connected_peers.add(node_address)

    # Try to establish P2P connection
    try:
        blockchain.node.connect_with_node('127.0.0.1', p2p_port)
    except:
        print(f"Failed to establish P2P connection with port {p2p_port}")

    return jsonify({'message': 'New node added successfully',
                    'total_nodes': list(blockchain.connected_peers)}), 201


@app.route('/list_product', methods=['POST'])
def list_product():
    json_data = request.get_json()
    required_fields = ['sender', 'product', 'amount']
    if not all(field in json_data for field in required_fields):
        return 'Listing data incomplete', 400

    # Create the transaction
    transaction = {
        'sender': json_data['sender'],
        'receiver': None,
        'product': json_data['product'],
        'amount': json_data['amount'],
        'type': 'list'
    }

    # Add to blockchain and broadcast
    index = blockchain.add_transaction(
        transaction['sender'],
        transaction['receiver'],
        transaction['product'],
        transaction['amount'],
        transaction['type']
    )

    response = {'message': f'Product will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/purchase_product', methods=['POST'])
def purchase_product():
    json_data = request.get_json()
    required_fields = ['buyer', 'seller', 'product']
    if not all(field in json_data for field in required_fields):
        return 'Purchase data incomplete', 400

    # Find and remove the listing
    for block in blockchain.chain:
        for i, transaction in enumerate(block['transactions']):
            if (transaction['type'] == 'list' and
                    transaction['sender'] == json_data['seller'] and
                    transaction['product'] == json_data['product']):
                # Add purchase transaction
                blockchain.add_transaction(
                    json_data['seller'],
                    json_data['buyer'],
                    json_data['product'],
                    transaction['amount'],
                    'purchase'
                )
                # Remove listing from transactions
                block['transactions'].pop(i)
                return jsonify({'message': 'Product purchased successfully!'}), 200

    return 'Product not found or not listed', 404


@app.route('/p2p/receive', methods=['POST'])
def receive_message():
    data = request.get_json()
    peer_id = request.remote_addr

    if data['type'] == "NEW_TRANSACTION":
        blockchain.transactions.append(data['transaction'])
        return jsonify({'message': 'Transaction received'}), 200
    elif data['type'] == "GET_CHAIN":
        blockchain.handle_get_chain(peer_id)
        return jsonify({'message': 'Chain requested'}), 200
    elif data['type'] == "CHAIN":
        blockchain.handle_chain(peer_id, data)
        return jsonify({'message': 'Chain received'}), 200

    return jsonify({'message': 'Unknown message type'}), 400


@app.route('/get_peers')
def get_peers():
    return jsonify({'peers': list(blockchain.connected_peers)}), 200


if __name__ == '__main__':
    # Determine Flask port based on P2P port
    flask_port = 8000 if args.port == 5001 else 8001
    app.run(host='0.0.0.0', port=flask_port, debug=True)