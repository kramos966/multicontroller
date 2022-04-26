from ..sock_encodeco import ZipEncoDeco
from .gen_image import test_image
import numpy as np

def protocol_test():
    encodeco = ZipEncoDeco()

    image = test_image()

    # Codifica la imatge
    compressed = encodeco.encode(image)

    # Decodifica-la
    decoded = encodeco.decode(compressed)

    print(f"Codification test: {np.allclose(decoded['data'], image)}")

if __name__ == "__main__":
    protocol_test()
