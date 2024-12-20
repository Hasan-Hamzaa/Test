# node.py
from flask import Flask, jsonify, request, render_template
from blockchain import Blockchain
import json
import argparse
import sqlite3

app = Flask(__name__)

# Command-line arguments for P2P port
parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=5001, help="Port for the blockchain node")
args = parser.parse_args()

blockchain = Blockchain(difficulty=2, port=args.port)


def get_all_listings():
    listings = []
    # Read from both databases (8000 and 8001)
    for port in [8000, 8001]:
        db_name = f'database_{port}.db'
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            # Get all active list-type transactions, ordered by newest first
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE type='list' AND id NOT IN (
                    SELECT t1.id FROM transactions t1
                    JOIN transactions t2 ON t1.product = t2.product 
                    AND t1.sender = t2.sender
                    WHERE t2.type='purchase'
                )
                ORDER BY id DESC
            """)

            transactions = cursor.fetchall()

            # Convert to dictionary format
            for tx in transactions:
                listing = {
                    'sender': tx[1],
                    'receiver': tx[2],
                    'product': tx[3],
                    'amount': tx[4],
                    'type': tx[5]
                }
                if listing not in listings:  # Avoid duplicates
                    listings.append(listing)

        except sqlite3.Error as e:
            print(f"Database error for {db_name}: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    return listings

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sell')
def sell_page():
    return render_template('sell.html')


@app.route('/buy')
def buy_page():
    listings = get_all_listings()
    return render_template('buy.html', listings=listings)


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
    try:
        # Get current port's database
        db_name = f'database_{blockchain.flask_port}.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Get blocks
        cursor.execute("SELECT * FROM blocks ORDER BY idx DESC")
        blocks = cursor.fetchall()

        # Get transactions
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC")
        transactions = cursor.fetchall()

        conn.close()

        formatted_blocks = []
        for block in blocks:
            formatted_blocks.append(blockchain.create_block_from_tuple(block))

        # Pass data to template with show_database flag
        return render_template('index.html', show_database=True, blocks=formatted_blocks, transactions=transactions)

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500


@app.route('/list_product', methods=['POST'])
def list_product():
    json_data = request.get_json()
    required_fields = ['sender', 'product', 'amount']
    if not all(field in json_data for field in required_fields):
        return 'Listing data incomplete', 400

    index = blockchain.add_transaction(json_data['sender'], None, json_data['product'], json_data['amount'], 'list')
    response = {'message': f'Product will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/purchase_product', methods=['POST'])
def purchase_product():
    json_data = request.get_json()
    required_fields = ['buyer', 'seller', 'product']
    if not all(field in json_data for field in required_fields):
        return 'Purchase data incomplete', 400

    # Try to find and process the purchase in both databases
    for port in [8000, 8001]:
        db_name = f'database_{port}.db'
        try:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            # Find the listing
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE sender = ? AND product = ? AND type = 'list'
                AND id NOT IN (
                    SELECT t1.id FROM transactions t1
                    JOIN transactions t2 ON t1.product = t2.product 
                    AND t1.sender = t2.sender
                    WHERE t2.type='purchase'
                )
            """, (json_data['seller'], json_data['product']))

            listing = cursor.fetchone()
            if listing:
                # Add purchase transaction
                blockchain.add_transaction(
                    json_data['seller'],
                    json_data['buyer'],
                    json_data['product'],
                    listing[4],  # amount
                    'purchase'
                )

                conn.commit()
                return jsonify({'message': 'Product purchased successfully!'}), 200

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if conn:
                conn.close()

    return 'Product not found or not listed', 404


@app.route('/get_peers')
def get_peers():
    return jsonify({'peers': list(blockchain.connected_peers)}), 200


@app.route('/receive_transaction', methods=['POST'])
def receive_transaction():
    data = request.get_json()
    if blockchain.receive_transaction(data['transaction']):
        return jsonify({'message': 'Transaction received and accepted'}), 200
    return jsonify({'message': 'Invalid transaction'}), 400


if __name__ == '__main__':
    flask_port = 8000 if args.port == 5001 else 8001
    app.run(host='0.0.0.0', port=flask_port, debug=True)