import matplotlib.pyplot as plt
import numpy as np

def colorize(array, a=(128, 128, 128), b=(1., 1.0, 1.00), c=(np.pi/3, 0, np.pi/2)):
    """Colorize a grayscale array using a cosine-based color mapper."""
    a = np.asarray(a)
    b = np.asarray(b)
    c = np.asarray(c)
    shape = array.shape
    if len(shape) > 2:
        raise ValueError("Array must be grayscale!")
    colored = np.zeros((*shape, 3), dtype=np.uint8)

    normalized = array-array.min()
    normalized[:] = normalized/normalized.max()
    colored[:, :, 0] = a[0]+127*np.cos(b[0]*2*np.pi*normalized+c[0])
    colored[:, :, 1] = a[1]+127*np.cos(b[1]*2*np.pi*normalized+c[1])
    colored[:, :, 2] = a[2]+127*np.cos(b[2]*2*np.pi*normalized+c[2])
    return colored

def test_image(n=1024):
    """Generate a nice image to use as a test."""
    y, x = np.mgrid[-n//2:n//2, -n//2:n//2]
    r2 = x*x+y*y
    sigma2 = n/4
    sigma2 *= sigma2
    phi = np.arctan2(y, x)
    image = np.sin(12*phi)*np.exp(-r2/sigma2)

    # Pinta la imatge...
    color_im = colorize(image)

    return color_im

