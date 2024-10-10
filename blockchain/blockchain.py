import hashlib
import json
import time
from urllib.parse import urlparse
from db_manager import MySQLManager
from config import DB_LOCALHOST, DB_USER, DB_PASS, DB_DATABASE

db_manager = MySQLManager(
    host=DB_LOCALHOST, user=DB_USER, password=DB_PASS, database=DB_DATABASE)
db_manager.connect()


class Blockchain:
    def __init__(self):
        self.last_block = {}
        self.pending_transactions = {}
        self.nodes = set()
        self.len = 0

        # genesis 블록 생성
        self.create_block(previous_hash='0')

    @staticmethod
    def hash(block):
        """hashing the block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # 블록생성
    def create_block(self, previous_hash):
        """Create the block"""
        if self.pending_transactions:
            block = {
                'timestamp': time.time(),
                'previous_hash': previous_hash,
                "date": self.pending_transactions.get('date'),
                "department": self.pending_transactions.get('department'),
                "name": self.pending_transactions.get('name'),
                "position": self.pending_transactions.get('position'),
                "time": self.pending_transactions.get('time')
            }
            self.pending_transactions = {}
            db_manager.insert_entrance_log(block['previous_hash'], block['timestamp'], block['date'], block['time']
                                           block['employee_id'], block['name'], block['position'], block['department'])

            self.last_block = block
            return True
        return False

    # 트랜젝션 추가
    def add_transaction(self, data):
        """Add the transaction"""
        self.pending_transactions = data

    # 노드 추가
    def add_node(self, node):
        """Add the node in 'nodes variable'"""
        self.nodes.add(node)

    def get_block_total(self):
        """Get total block count"""
        return db_manager.get_total_count()

    def search_block(self, date, name, department):
        """Find blocks matching search data"""
        results = db_manager.search_data(date, name, department)
        if not results:
            return False
        for result in results:
            result['date'] = str(result['date'])
            result['time'] = str(result['time'])
        return results
