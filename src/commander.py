import socket
import multiprocessing as mp
import imageio
import numpy as np
from .devices import BasicDevice

help_text = \
"""Available commands:
    connect [ip] [port]           - connect to device at ip through port.
    set [numerator] [denominator] - set the exposure time T = numerator/denominator.
    capture {number}              - capture an image with optional argument the number of the camera to be used.
    exit                          - close all connections and exit
"""

class CommanderDevice(BasicDevice):
    def __init__(self, timeout=0.5):
        super().__init__()
        self.connections = {}
        self.busy_queue = mp.Queue()
        self.running = True
        self.timeout = timeout

        # Timeout de les operacions
        if timeout:
            socket.setdefaulttimeout(timeout)

    def put_text(self, text):
        """Funció per a ser extesa. Rep un text i l'imprimeix amb el mètode que s'especifiqui..."""
        print(text)

    def save_image(self, fname, image):
        """Funció per a ser extesa. Mètode per a desar una imatge."""
        imageio.imsave(fname, np.uint8(255*image))

    def input_text(self):
        """Funció per a ser extesa. Captura de text per part de l'usuari..."""
        text = input("> ")
        return text

    def add_connection(self, process, host, queue):
        self.connections[host] = process, queue

    def add_camera(self, process, host, queue):
        """Extensible."""
        self.add_connection(process, host, queue)

    def connect_server(self, host, port):
        if not (host in self.connections):
            # Creem un subprocés per al host que el controlarà
            command_queue = mp.Queue()
            p = mp.Process(target=self.poll_server, 
                           args=(host, port, command_queue, 
                               self.busy_queue))
            # Comencem a escoltar
            p.start()
            # Comprovem si la connexió ha sigut efectiva...
            if self.timeout:
                p.join(timeout=self.timeout*1.5) # Espera 200 ms per a veure si s'ha acabat...
            else:
                p.join(timeout=0.2)
            if p.is_alive():
                # Lliguem la connexió si tot ha sortit bé!
                self.add_camera(p, host, command_queue)
                self.put_text(f"Successful connection with {host}!")


    def poll_server(self, host, port, queue, busy_queue):
        # Continuously poll server until finished
        ip = host.split()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.connect((host, port))
                # Comencem a treballar
                working = True
                while working:
                    # Si no hi ha res a la cua, següent iteració
                    if queue.empty():
                        continue
                    command = queue.get()
                    if command == "close":
                        working = False
                        self.send_response(server, command)
                        continue    # Passem a la següent iteració, trencant el bucle
                    self.send_response(server, command)
                    # Escoltem el servidor per a veure què ens diu
                    listening = True
                    # Indiquem que s'està processant el missatge del servidor
                    busy_queue.put("busy")
                    while listening:
                        msg_recv = self.receive_message(server)
                        # Cas missatge
                        if msg_recv["msg_kind"] == "message":
                            message = msg_recv["message"]
                            # Si rebem un none, deixem d'escoltar el servidor.
                            if message == "none":
                                listening = False
                            else:
                                self.put_text(f"<{host}>: {msg_recv['message']}")
                            # Enviem confirmació
                        # Cas Array
                        elif msg_recv["msg_kind"] == "array":
                            array = msg_recv["data"]
                            self.save_image(f"{ip[-1]}.png", array)
                        self.acknowledge_command(server)
                    busy_queue.get()    # Indiquem que aquest fil ja no està ocupat rebent dades
                self.put_text(f"Connection ended with <{host}>")
        except:
            self.put_text(f"Error: <{host}> {port} does not exist!")

    def send_command(self, host, command):
        try:
            p, queue = self.connections[host]
            queue.put(command)
        except:
            self.put_text("Error: <{host}> does not exist!")

    def send_all(self, command):
        for host in self.connections:
            print(host)
            self.send_command(host, command)

    def close_connection(self, host):
        try:
            p, queue = self.connections[host]
        except:
            self.put_text(f"Connection with {host} does not exist.")
            # Surt de la funció ja que el codi no és correcte...
            return

        # Send closing connection signal to the server
        queue.put("close")
        p.join()

    def close_all(self):
        for host in self.connections:
            self.close_connection(host)

    def check_ports(self, command):
        if self.running:
            args = command.split(" ")
            if args[0] == "connect":
                try:
                    host, port = args[1], int(args[2])
                except:
                    self.put_text("Error: connect [host] [port]")
                    return

                self.connect_server(host, port)

            elif args[0] == "capture":
                if not self.connections:
                    self.put_text("Error: No camera(s) connected!")
                    return
                elif len(args) == 2:
                    cam = args[1]
                    if cam in self.connections.keys():
                        self.send_command(cam, args[0])
                elif len(args) == 1:
                    self.send_all(args[0])
                else:
                    self.put_text("Error: capture (host).")
            elif args[0] == "set":
                if not self.connections:
                    self.put_text("Error: No camera(s) connected!")
                    return
                elif len(args) < 2:
                    self.put_text("Error: set shutter [time]")
                else:
                    self.send_all(command)

            elif args[0] == "help":
                self.put_text(help_text)

            elif args[0] == "exit":
                self.running = False
                # Tanca totes les connexions
                self.close_all()
            else:
                self.put_text("Unrecognized command")

    def run(self):
        command = input("> ")
        while self.running:
            self.check_ports()

def main():
    commander = CommanderDevice()
    commander.run()

if __name__ == "__main__":
    main()
