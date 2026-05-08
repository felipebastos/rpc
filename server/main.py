import time

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from datetime import datetime

counter = 0


def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] server {message}", flush=True)


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)

    def do_POST(self):
        self.server.current_client = (
            f"{self.client_address[0]}:{self.client_address[1]}"
        )
        log(f"HTTP POST {self.path} from {self.server.current_client}")
        super().do_POST()

    def log_message(self, format, *args):
        pass


class LoggingXMLRPCServer(SimpleXMLRPCServer):
    current_client = "unknown"

    def _dispatch(self, method, params):
        log(f"<- {self.current_client} {method}{params}")
        try:
            result = super()._dispatch(method, params)
        except Exception as error:
            log(f"!! {self.current_client} {method} failed: {error}")
            raise

        log(f"-> {self.current_client} {method} = {result}")
        return result


# Create server
with LoggingXMLRPCServer(("0.0.0.0", 8000), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    # Register pow() function; this will use the value of
    # pow.__name__ as the name, which is just 'pow'.
    server.register_function(pow)

    # Register a function under a different name
    def adder_function(x, y):
        return x + y

    server.register_function(adder_function, "add")

    # Register an instance; all the methods of the instance are
    # published as XML-RPC methods (in this case, just 'mul').
    class MyFuncs:
        def mul(self, x, y):
            return x * y

    server.register_instance(MyFuncs())

    def slow_add(x, y):
        time.sleep(10)
        return x + y

    server.register_function(slow_add, "slow_add")

    def increment():
        global counter
        counter += 1
        log(f"Contador mudou para {counter}")
        time.sleep(5)
        return counter

    server.register_function(increment, "increment")

    # Run the server's main loop
    log("listening on 0.0.0.0:8000 at /RPC2")
    server.serve_forever()
