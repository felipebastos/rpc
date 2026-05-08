import xmlrpc.client
from datetime import datetime
import os
import socket
import time

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
for attempt in range(1, 11):
    try:
        log(f"connecting to {server_url} (attempt {attempt})")
        call(server, "pow", 2, 3)
        # server.pow(2,3)
        log(f"connected to {server_url}")
        break
    except OSError:
        if attempt == 10:
            raise
        log("server not ready yet; retrying in 1s")
        time.sleep(1)

call(server, "slow_add", 2, 3)
call(server, "mul", 5, 2)

# Print list of available methods
call(server.system, "listMethods")
