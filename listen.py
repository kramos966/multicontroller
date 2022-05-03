from src import ListenerDevice
from imcapture import capture_image, CameraApp

class PicameraListener(ListenerDevice):
    def __init__(self, host, port):
        # Inicialització de la classe mare
        ListenerDevice.__init__(self, host, port)

        # Crea una instància de càmera
        self.camera = CameraApp()

    def close(self):
        self.camera.close()
    
    def set_shutter(self, speed):
        return self.camera.set_shutter_speed(speed)

    def capture(self, *args, **kwargs):
        """Aquesta és una funció que s'ha d'extendre amb el mètode de captura
        desitjat!. Ha de retornar obligatòriament un array."""
        # Fem un wrapper amb la funció que hem generat nosaltres...
        self.camera.capture()
        return self.camera.image.copy()

if __name__ == "__main__":
    host, port = "0.0.0.0", 8888
    listener = PicameraListener(host, port)
    listener.listen()
