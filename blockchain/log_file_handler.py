# log_file_handler.py
from watchdog.events import FileSystemEventHandler
import requests
from config import LOGFILE, LOG_UPLOAD_URL
import os  # os 모듈을 추가합니다.


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


# 커스텀 핸들러 정의
class LogServerHandler(logging.Handler):
    def __init__(self, server_url, log_file_name):
        super().__init__()
        self.server_url = server_url
        self.log_file_name = log_file_name

    def emit(self, record):
        log_entry = self.format(record)
        try:
            # 로그 메시지와 로그 파일 이름을 함께 전송
            response = requests.post(self.server_url, json={
                'log': log_entry,
                'file_name': self.log_file_name
            })
            if response.status_code != 200:
                print(f"Failed to send log entry. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error while sending log entry: {e}")
