import socket
import numpy as np
import multiprocessing
import json
from .devices import BasicDevice

class ListenerDevice(BasicDevice):
    """Listener device que només funciona amb objectes json"""
    def __init__(self, host, port, timeout=1.):
        super().__init__()
        self.host, self.port = host, port

        self.timeout = timeout

    def stop_signal(self, conn):
        self.send_response(conn, "none")

    def capture(self, *args, **kwargs):
        """Funció per a ser extesa, aquesta és només una dummy. Mètode de captura d'una
        imatge de la càmera. Ha de retornar un array"""
        array = np.random.rand(512, 512, 3).astype(np.float32)
        return array

    def signal_process(self, conn, fun, message=None, rsp_head="", fun_args=None):
        """Realitza l'operació fun tot avisant al client de què es realitzarà."""
        self.acknowledge_command(conn)
        if message:
            self.send_response(conn, message)
        if fun_args:
            result = fun(*fun_args)
        else:
            result = fun()
        if isinstance(result, np.ndarray):
            # Enviem un array com a resposta
            self.send_response(conn, result)
            self.send_response(conn, "Fet!")
        else:
            self.send_response(rsp_head, str(result))
        self.stop_signal(conn)

    def process_conn(self, conn):
        """Processa una connexió, segons les ordres que rebi!"""
        # Recupera el missatge sencer
        working = True
        while working:
            msg_dict = self.receive_message(conn)
            if msg_dict["msg_kind"] == "message":
                message = msg_dict["message"]
                print(message)
                args = message.split(" ")
                if args[0] == "close":
                    self.acknowledge_command(conn)
                    working = False
                    #self.stop_signal(conn)

                elif args[0] == "capture":
                    # FIXME: De vegades, no es processa la captura...
                    self.signal_process(conn, self.capture, "Capturo i envio una imatge...")

                elif args[0] == "set":
                    if len(args) < 3:
                        print("Bad command, 'set' requires at least 2 more arguments!")
                    else:
                        kind, option = args[1:]
                        if kind == "shutter":
                            option = [int(i) for i in option] 
                            self.signal_process(conn, self.set_shutter, rsp_head="Shutter set to",
                                    fun_args=(option,))

                else:
                    self.ackowledge_command(conn, "vale.")
                    self.stop_signal(conn)

    def close(self):
        pass

    def set_shutter(self, option):
        pass

    def listen(self):
        self.running = True
        # Obre un socket per a sentir connexions
        print("Begin listening...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.host, self.port))
                while self.running:
                    # Busquem connexions entrants
                    s.listen()
                    conn, addr = s.accept()
                    with conn:
                        print(f"Accepted {addr}")
                        working = True
                        self.process_conn(conn)
                    print(f"Connection closed with {addr}")
            except KeyboardInterrupt:
                print(f"Stopped listening on {self.host}, {self.port}")
        # Close on exit
        self.close()

def main():
    host, port = "0.0.0.0", 8888
    listener = ListenerDevice(host, port)
    listener.listen()

if __name__ == "__main__":
    main()
