import numpy as np
from .sock_encodeco import encode_bytes, recover_bytes, ZipEncoDeco

buff = 1024*1024

class BasicDevice:
    def __init__(self):
        self._encodeco = ZipEncoDeco()

    def send_bytes(self, sock, message):
        encoded = encode_bytes(message)
        sock.sendall(encoded)


    def send_message(self, sock, message):
        # Comprimim el missatge
        msg_bytes = self._encodeco.encode(message)
        # Els enviem
        self.send_bytes(sock, msg_bytes)

    def acknowledge_command(self, conn):
        self.send_message(conn, "vale")

    def send_response(self, sock, message):
        self.send_message(sock, message)
        # Rebem la confirmació
        self.receive_message(sock)

    def receive_message(self, sock):
        complete = False
        data = b''
        while not complete:
            data += sock.recv(buff)
            # Un cop rebem totes les dades, sortim!
            if recovered := recover_bytes(data):
                complete = True
        # Decodifiquem el missatge com cal. 
        decoded = self._encodeco.decode(recovered)    # És un diccionari!
        return decoded
