from picamera import PiCamera
import numpy as np

class CameraApp():
    def __init__(self, resolution=None):
        if resolution:
            w, h = resolution
            # Restringim les dimensions a múltiples de 32 i 16 respectivament!
            w = w & (~31)
            h = h & (~15)

        else:
            w, h = 1024, 768
        
        # Array on es captura cada imatge. Format RGB
        self.image = np.zeros((h, w, 3), dtype=np.uint8)
        # Iniciem la càmera...
        self.cam = PiCamera()
        self.cam.resolution = (w, h)
        self.cam.framerate = (1, 1) # FIXME: Fes-lo variable!!!!!

    def set_shutter_speed(self, speed):
        """Canvia la velocitat de l'obturador segons el temps en us en que triga
        a capturar una imatge del sensor sencer.
        """
        self.cam.shutter_speed = speed
        return self.cam.shutter_speed

    def close(self):
        self.cam.close()

    def set_resolution(self, resolution):
        w, h = resolution
        # Restringim les dimensions a múltiples de 32 i 16 respectivament!
        w = w & (~31)
        h = h & (~15)

        self.image = np.zeros((h, w, 3), dtype=np.uint8)
        self.cam.resolution = (w, h)
        return w, h

    def capture(self):
        selrf.cam.capture(self.array, "rgb")

def capture_image(*args, **kwargs):
    """Captura una imatge i la guarda en un array."""
    #res = (4056//2, 3040//2)
    res = (1024*2, 768*2)
    with PiCamera() as cam:
        cam.resolution = res
        array = np.empty((*res[::-1], 3), dtype=np.uint8)
        cam.capture(array, "rgb")
    return array

if __name__ == "__main__":
    array = capture_image()
