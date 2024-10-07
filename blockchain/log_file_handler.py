# log_file_handler.py
from watchdog.events import FileSystemEventHandler
import requests
from config import LOGFILE, LOG_UPLOAD_URL
import os  # os 모듈을 추가합니다.


class LogFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == LOGFILE:
            if not os.path.exists(LOGFILE):
                open(LOGFILE, 'w').close()

            with open(LOGFILE, 'rb') as f:
                files = {'file': f}
                response = requests.post(LOG_UPLOAD_URL, files=files)
                if response.status_code == 200:
                    print("로그 파일이 성공적으로 전송되었습니다.")
                else:
                    print("로그 파일 전송 실패:", response.text)
