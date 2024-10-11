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
                    print(f"Failed to send log entry. Status code: {
                          response.status_code}")
            except Exception as e:
                print(f"Error while sending log entry: {e}")

    def stop(self):
        self.log_queue.put(None)  # 스레드 종료를 위해 None 추가
        self.thread.join()  # 스레드가 종료될 때까지 대기


def setup_logging(log_file_path, server_url):
    logging.basicConfig(filename=log_file_path,
                        filemode='w', level=logging.INFO)
    logger = logging.getLogger()

    log_server_handler = LogServerHandler(
        server_url, log_file_path.split('/')[-1])
    log_server_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    log_server_handler.setFormatter(formatter)
    logger.addHandler(log_server_handler)

    return logger
