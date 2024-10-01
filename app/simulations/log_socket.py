"""
Класс для работы с сокетом отправки сообщений о ходе расчета
"""
import sys
import socket
import time

def follow(thefile):
    """
    Функция-генератор для проверки лог-файла с периодичностью в 0.1 секунду
    """
    thefile.seek(0,2) # Go to the end of the file
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def transmit_log(host_: str, port_: int, log_file_path_: str):
    """
    Основная функция, в которой создается сокет и происходит передача логов
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
    try:
        sock.connect((host_, port_))  # подключемся к серверному сокету
    except ConnectionError:
        sock.close()
        exit(1)
    except socket.gaierror:
        sock.close()
        exit(1)
    with open(log_file_path_) as logfile:
    # logfile = open(log_file_path_)
        lines = follow(logfile)
        for line in lines:
            sock.send(bytes(line, encoding = 'UTF-8'))
            if line.strip().endswith('END OF JOB'):
                break
        sock.close()


if __name__ == "__main__":
    host = sys.argv[1]
    port = sys.argv[2]
    log_file_path = sys.argv[3]
    transmit_log(host_=host, port_=int(port), log_file_path_=log_file_path)
