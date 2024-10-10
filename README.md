# ChainGATE

블록체인을 이용한 출입관리시스템\_충북대학교 졸업작품

# version

2024.07.09 - version 1.0.0

# Setting

❗**최소 3개 이상의 우분투 서버가 필요함**

❗각 서버는 노드로 지칭하고, 모든 노드는 아래의 동일한 세팅이 필요함

### 1. 필요 프로그램 설치 및 설정

```
$ sudo apt update

### ufw 활성화 및 포트 설정
$ sudo apt install ufw -y
$ sudo ufw allow ssh, mysql, 5000       # 22, 3306, 5000 포트
$ sudo ufw enable
$ sudo ufw status

### python 및 관련 모듈 설치
$ sudo apt install python3 python3-pip -y
$ sudo pip3 install flask
$ sudo pip3 install pyopenssl
$ sudo pip3 install mysql-connector-python


### openssl 설치 및 개인키, CSR 발급
$ sudo apt install openssl -y              # openssl 설치
$ sudo mkdir certs
$ sudo openssl genrsa -out certs/node_private_key.pem 2048
$ sudo openssl req -new -key certs/node_private_key.pem -out certs/node_csr.pem
```

### 2. DB 설치 및 설정

```
### MySQL 설치 및 실행
$ sudo apt install mysql-server -y
$ sudo systemctl status mysql
$ sudo systemctl start mysql        # 실행되고 있지 않을 경우

### DB setting
$ sudo mysql -u root -p
mysql> CREATE DATABASE chaingate;
mysql> USE chaingate;
mysql> CREATE TABLE entrance_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    previous_hash CHAR(64) NOT NULL,
    timestamp DOUBLE NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    employee_id VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL
);
mysql> CREATE USER '{username}'@'localhost' IDENTIFIED BY 'password';
mysql> GRANT SELECT, INSERT ON chaingate.entrance_log TO '{username}'@'localhost';
mysql> FLUSH PRIVILEGES;
```

### 3. Git Repository 및 필요 파일 생성

```
$ sudo apt install git -y
$ git clone https://github.com/DDongu/ChainGATE.git
$ cd /ChainGATE/blockchain
$ vi config.py      # 아래 config.py 파일을 각 노드 환경에 맞게 작성
$ vi register.py    # 아래 register.py 파일을 각 노드 환경에 맞게 작성
```

_config.py_

```
### at 192.168.0.29 노드 ###
CA_ADDRESS = 'ca-server-address'                    # ip+port
CSR_PATH = '/home/node1/certs/node_csr.pem'         # hostname is different
NODE_CERT_PATH = '/home/node1/certs/node_cert.pem'  # hostname is different
CSR_URL = f'http://{CA_ADDRESS}/api/v1/cert/request'
VERIFY_URL = f'http://{CA_ADDRESS}/api/v1/cert/verify'
REVOKE_URL = f'http://{CA_ADDRESS}/api/v1/cert/revoke'
STATUS_URL = f'http://{CA_ADDRESS}/api/v1/cert/status'
DB_LOCALHOST = 'localhost'
DB_USER = 'db-username'
DB_PASS = 'db-password'
DB_DATABASE = 'chaingate'
PORT=5000
```

_register.py_

```
### at 192.168.0.29 노드 ###
import requests
from config import PORT, NODE_CERT_PATH

"""Register yourself by requesting the /nodes/register
nodes = ['192.168.0.29', '192.168.0.30']
with open(NODE_CERT_PATH, 'r') as f:
    cert = f.read()
data = {'cert': cert}

for node in nodes:
    response = requests.post(f'http://{node}:{PORT}/nodes/register', json=data)
    print(f'{node}:{PORT}  :', end='')
    print(response.json())
```

# How to start the Blockchain server

```
$ cd /ChainGATE/blockchain
$ nohup sudo python3 -u blockAPI.py > ~/nohup.out 2>&1 &

### After running blockAPI.py on every nodes
$ python3 register.py

### Log file
$ cat ~/nohup.out
```

# Blockchain API GUIDE

### 1. nodes/register [POST]

    { "cert": cert }

|  Key   |         Value         |   Type    |
| :----: | :-------------------: | :-------: |
| "cert" | CA를 통해 받은 인증서 | .pem 파일 |

**❗각 노드의 register.py를 통해서 사용**

### 2. transaction/new [POST]

_❗모든 노드에 동시에 보내져야 됨_

    {
        "date": "2024-04-12",
        "time": "10:30:00",
        "employee_id": "2019038999"
        "name": "홍길동",
        "position": "팀원",
        "department": "개발부"
    }

|     Key      |    Value    |        Type         |
| :----------: | :---------: | :-----------------: |
|    "date"    |  출입날짜   | String [YYYY-MM-DD] |
|    "time"    |  출입시간   |  String [HH:MM:SS]  |
|    "employee_id"    | 사번 |       String        |
|    "name"    | 출입자 이름 |       String        |
|  "position"  | 출입자 직급 |       String        |
| "department" | 출입자 소속 |       String        |

### 3. chain/search [POST]

    {
        "date": "2024-04-12",
        "name": "",
        "department": "개발부"
    }

|     Key      |    Value    |           Type            |
| :----------: | :---------: | :-----------------------: |
|    "date"    |  출입날짜   | String [YYYY-MM-DD] OR "" |
|    "name"    | 출입자 이름 |       String OR ""        |
| "department" | 출입자 소속 |       String OR ""        |

**❗ 데이터가 없을 경우, _Value=""_ (최소 1개 이상의 데이터는 있어야 됨).**
