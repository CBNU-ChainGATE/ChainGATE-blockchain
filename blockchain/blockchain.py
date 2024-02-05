import datetime
import hashlib
import json
from urllib.parse import urlparse
import requests


class Blockchain:

    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.create_block(proof=1, previous_hash='0', data='none')

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # 새로운 블록 생성
    def create_block(self, proof, previous_hash, data):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'data': data,  # json 형태의 데이터
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block

    # 이전 블록 가져오기
    def get_previous_block(self):
        return self.chain[-1]

    # 작업 증명 과정
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operations = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operations.startswith('0000'):
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    # 블록 해쉬화
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # 증명되지 않은 블록이 있는지 확인
    def is_valid_chain(self, chain):
        previous_block = chain[0]
        block_index = 1

        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()

            if not hash_operation.startswith('0000'):
                return False

            previous_block = block
            block_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            url = 'http://%s/chain' % (node)
            print('url: ' + url)
            response = requests.post(url, data={"type": "1"})

            if response.status_code == 200:
                chain = response.json()['chain']
                length = response.json()['length']

                if length > max_length and self.is_valid_chain(chain):
                    print("if문 통과")
                    max_length = length
                    new_chain = chain

        print("new_chain", end='')
        print(new_chain)
        if new_chain:
            self.chain = new_chain
            return True

        return False
