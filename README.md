Blockchain-Based Decentralized Marketplace
A Python-based blockchain project that facilitates a decentralized marketplace using peer-to-peer networking, blockchain technology, and a RESTful Flask API. This project enables secure, transparent, and tamper-proof transactions for listing and purchasing products in a distributed environment.

📝 Table of Contents
Features
Technologies
Project Structure
Requirements
Installation
Usage
API Endpoints
Contributors
License
🌟 Features
Blockchain Technology: Implements Proof of Work (PoW) for block validation.
Decentralized Network: Nodes communicate via a P2P network for syncing blockchain and transactions.
User-Friendly Marketplace: Interfaces for listing products, buying items, and managing inventory.
Data Persistence: Each node maintains its blockchain and transactions using SQLite databases.
RESTful API: Offers endpoints to interact with the blockchain and manage transactions.
🛠 Technologies
Programming Language: Python
Framework: Flask
Database: SQLite
Networking: Peer-to-Peer (p2pnetwork library)
📂 Project Structure
plaintext
Copy
├── blockchain.py         # Core blockchain and network logic
├── node.py               # Flask-based API and web interface
├── templates/            # HTML templates for web interface
├── static/               # Static assets (CSS, JS, images)
├── requirements.txt      # List of dependencies
└── README.md             # Project documentation
📋 Requirements
Python 3.8 or later
Flask
SQLite
Requests library
p2pnetwork library
🚀 Installation
Clone the repository:

bash
Copy
git clone https://github.com/your-repository-name.git
cd your-repository-name
Install dependencies:

bash
Copy
pip install -r requirements.txt
Run the project: Start a blockchain node using:

bash
Copy
python node.py --port <PORT>
Replace <PORT> with the port number for your node. For example:

bash
Copy
python node.py --port 5001
python node.py --port 5002
Access the web interface: Open your browser and navigate to:

arduino
Copy
http://127.0.0.1:<FLASK_PORT>
Replace <FLASK_PORT> with the corresponding Flask port (e.g., 8000 for port 5001).

💡 Usage
Web Interface
Sell Products: Navigate to /sell to list a product for sale.
Buy Products: Navigate to /buy to view and purchase available items.
View Transactions and Blocks: Visit /view_database to inspect blockchain and transaction history.
Monitor Network Activity: View connected peers and activity at /network_activity.
Blockchain Operations
Mine a Block: Trigger mining with the /mine_block endpoint.
Check Blockchain Validity: Use the /is_valid endpoint to verify data integrity.
🔗 API Endpoints
Blockchain Management
GET /get_chain: Retrieve the blockchain.
GET /is_valid: Check if the blockchain is valid.
Transaction Management
POST /list_product: List a product for sale.
Parameters:

sender: The user listing the product.
product: The name of the product.
amount: The price of the product.
POST /purchase_product: Purchase a product.
Parameters:

buyer: The user buying the product.
seller: The seller of the product.
product: The product being purchased.
GET /get_latest_transactions: Get the most recent transactions.

Node Management
POST /register_node: Register a new node in the network.
Parameters:

address: The address of the node.
p2p_port: The port number for the P2P connection.
GET /get_peers: Get the list of connected peers.
