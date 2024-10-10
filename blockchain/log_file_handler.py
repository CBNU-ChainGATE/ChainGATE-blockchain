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
import aiohttp
import asyncio

class LogServerHandler(logging.Handler):
    def __init__(self, server_url, log_file_name):
        super().__init__()
        self.server_url = server_url
        self.log_file_name = log_file_name

    async def send_log(self, log_entry):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.server_url, json={
                    'log': log_entry,
                    'file_name': self.log_file_name
                }) as response:
                    if response.status != 200:
                        print(f"Failed to send log entry. Status code: {response.status}")
            except Exception as e:
                print(f"Error while sending log entry: {e}")

    def emit(self, record):
        log_entry = self.format(record)

        # 현재 이벤트 루프를 가져오고, 없으면 새로 생성
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # 현재 루프가 없으면
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # 비동기 작업으로 로그 전송
        loop.create_task(self.send_log(log_entry))

def setup_logging(log_file_path, server_url):
    logging.basicConfig(filename=log_file_path, filemode='w', level=logging.INFO)
    logger = logging.getLogger()

    log_server_handler = LogServerHandler(server_url, log_file_path.split('/')[-1])
    log_server_handler.setLevel(logging.INFO)
    logger.addHandler(log_server_handler)

    return logger
