import sys
import socket
import time

def follow(thefile):
    thefile.seek(0,2) # Go to the end of the file
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1) # Sleep briefly
            continue
        yield line

def transmit_log(host: str, port: int, log_file_path: str):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
    sock.connect((host, port))  # подключемся к серверному сокету
    logfile = open(log_file_path)
    lines = follow(logfile)
    for line in lines:
        # line = line.strip()
        # print(line)
        sock.send(bytes(line, encoding = 'UTF-8'))
        if line.strip().endswith('END OF JOB'):
                break


if __name__ == "__main__":
    host = sys.argv[1]
    port = sys.argv[2]
    log_file_path = sys.argv[3]
    transmit_log(host=host, port=int(port), log_file_path=log_file_path)
