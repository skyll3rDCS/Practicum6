import socket
import logging
from pr_6_settings import WebSettings
from threading import Thread
from datetime import datetime
from pathlib import Path
from os.path import exists

def get_response(error, text, file_type):
    return f"""HTTP/1.1 {error} {WebSettings.stat[error]}
Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S GTM')}
Server: {WebSettings.name}
Content-Type: {WebSettings.types[file_type]}
Content-Length: {len(text)}
Connection: close
""".encode() + text

def main_handler(request, addr):
    try:
        current_file = request.split('\n')[0].split()[1][1:]
    except:
        current_file = 'index.html'
    if not current_file:
        current_file = 'index.html'
    main_path = Path(WebSettings.directory, current_file)
    if exists(main_path):
        file_type = current_file.split(".")[-1]
        if file_type in WebSettings.types:
            error = '200'
            write_log(error, addr, main_path)
            with open(main_path, "rb") as file:
                text = file.read()
            response = get_response(error, text, file_type)
            return response
        else:  # неразрешенный тип
            error = '403'
            text = "<h1>403</h1>".encode()
            file_type = 'html'
            write_log(error, addr, main_path)
            response = get_response(error, text, file_type)
            return response

    elif not exists(main_path) or current_file == '':
        error = '404'
        text = "<h1>404</h1>".encode()
        file_type = 'html'
        write_log(error, addr, main_path)
        response = get_response(error, text, file_type)
        return response

def get_connection(conn, addr):
    with conn:
        data = conn.recv(WebSettings.max_size)
        if data == b"":
            conn.close()
        request = data.decode()
        print(request)
        resp = main_handler(request, addr)
        conn.send(resp)


def write_log(error, addr, text):
        logging.info(f"""IP-address: {addr} File path: {text} Code: {error} """)



def log_Info():
    logging.basicConfig(
        level=logging.DEBUG,
        format="Date: %(asctime)s | %(message)s",
        handlers=[
            logging.FileHandler("logs.log"),
            logging.StreamHandler(),
        ],
    )

def main_web():
    log_Info()
    sock = socket.socket()
    try:
        sock.bind(('', WebSettings.port))
        print('Using port: ', WebSettings.port)
    except OSError:
        sock.bind(('', WebSettings.other_port))
        print('Using port: ', WebSettings.other_port)
    sock.listen(5)
    while True:
        conn, addr = sock.accept()
        print("Connected", addr)
        Thread(target=get_connection, args=[conn, addr[0]]).start()

if __name__ == '__main__':
    main_web()
