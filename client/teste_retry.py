import xmlrpc.client
from datetime import datetime
import os
import socket
import time

socket.setdefaulttimeout(2)


server_url = os.getenv("SERVER_URL", "http://localhost:8000/RPC2")
client_name = os.getenv("CLIENT_NAME", socket.gethostname())


def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] client:{client_name} {message}", flush=True)


def call(server, method_name, *args):
    log(f"-> {method_name}{args}")
    result = getattr(server, method_name)(*args)
    log(f"<- {method_name} = {result}")
    return result


server = xmlrpc.client.ServerProxy(server_url)
for attempt in range(1, 3):
    try:
        log(f"calling increment attempt {attempt}")
        call(server, "increment")
        break
    except OSError as error:
        log(f"increment failed: {error}; retrying")
