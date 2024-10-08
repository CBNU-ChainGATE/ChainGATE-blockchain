# log_file_handler.py
# from watchdog.events import FileSystemEventHandler
# import requests
# from config import LOGFILE, LOG_UPLOAD_URL
# import os  # os 모듈을 추가합니다.


# class LogFileHandler(FileSystemEventHandler):
#     def on_modified(self, event):
#         if event.src_path == LOGFILE:
#             if not os.path.exists(LOGFILE):
#                 open(LOGFILE, 'w').close()

#             with open(LOGFILE, 'rb') as f:
#                 files = {'file': f}
#                 response = requests.post(LOG_UPLOAD_URL, files=files)
#                 if response.status_code == 200:
#                     print("로그 파일이 성공적으로 전송되었습니다.")
#                 else:
#                     print("로그 파일 전송 실패:", response.text)


# import logging
# import requests

# class LogServerHandler(logging.Handler):
#     def __init__(self, server_url, log_file_name):
#         super().__init__()
#         self.server_url = server_url
#         self.log_file_name = log_file_name

#     def emit(self, record):
#         log_entry = self.format(record)
#         try:
#             # 로그 메시지와 로그 파일 이름을 함께 전송
#             response = requests.post(self.server_url, json={
#                 'log': log_entry,
#                 'file_name': self.log_file_name
#             })
#             if response.status_code != 200:
#                 print(f"Failed to send log entry. Status code: {response.status_code}")
#         except Exception as e:
#             print(f"Error while sending log entry: {e}")

# def setup_logging(log_file_path, server_url):
#     logging.basicConfig(filename=log_file_path, filemode='w', level=logging.INFO)
#     logger = logging.getLogger()

#     # 로그 서버로 로그를 보내는 핸들러 추가 (파일 이름 포함)
#     log_server_handler = LogServerHandler(server_url, log_file_path.split('/')[-1])
#     log_server_handler.setLevel(logging.INFO)
#     logger.addHandler(log_server_handler)

#     return logger


import logging
import requests
import threading
import queue

class LogServerHandler(logging.Handler):
    def __init__(self, server_url, log_file_name):
        super().__init__()
        self.server_url = server_url
        self.log_file_name = log_file_name
        self.log_queue = queue.Queue()
        self.thread = threading.Thread(target=self.process_logs)
        self.thread.start()

    def emit(self, record):
        log_entry = self.format(record)
        self.log_queue.put(log_entry)

    def process_logs(self):
        while True:
            log_entry = self.log_queue.get()
            if log_entry is None:  # None을 받으면 종료
                break
            try:
                response = requests.post(self.server_url, json={
                    'log': log_entry,
                    'file_name': self.log_file_name
                })
                if response.status_code != 200:
                    print(f"Failed to send log entry. Status code: {response.status_code}")
            except Exception as e:
                print(f"Error while sending log entry: {e}")

    def stop(self):
        self.log_queue.put(None)  # 스레드 종료를 위해 None 추가
        self.thread.join()  # 스레드가 종료될 때까지 대기

def setup_logging(log_file_path, server_url):
    logging.basicConfig(filename=log_file_path, filemode='w', level=logging.INFO)
    logger = logging.getLogger()

    log_server_handler = LogServerHandler(server_url, log_file_path.split('/')[-1])
    log_server_handler.setLevel(logging.INFO)
    logger.addHandler(log_server_handler)

    return logger
