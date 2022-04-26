from .numpy_json import NumpyEncoder, NumpyDecoder
import numpy as np
import zlib
endianness = "little"

class EncodingError(Exception):
    pass

def encode_bytes(byte_arr):
    """Codifica un array de bytes amb una capçalera indicant-ne la longitud."""
    length = len(byte_arr)
    header = length.to_bytes(4, endianness)

    coded = header+byte_arr

    return coded

def recover_bytes(byte_arr):
    if len(byte_arr) < 4:
        return None
    else:
        length = int.from_bytes(byte_arr[:4], byteorder=endianness)
        msg_len = len(byte_arr)-4
        if msg_len < length:
            return None
        else:
            return byte_arr[4:]

class ZipEncoDeco():
    """Wrapper per a codificar i decodificar objectes a strings de json i
    vice-versa."""
    def __init__(self):
        self._nencoder = NumpyEncoder()
        self._ndecoder = NumpyDecoder()

    def encode(self, obj):
        """Codificador d'objectes segons els tipus acceptats..."""
        # Si no és un array, el tractem diferent...
        if not isinstance(obj, np.ndarray):
            if isinstance(obj, str):
                target = {"msg_kind": "message",
                            "message": obj}
            else:
                raise EncodingError(f"Type {type(message)} not supported!")
        else:
            target = obj

        target_bytes = self._nencoder.encode(target).encode("ascii")
        # Compressió zip
        compressed = zlib.compress(target_bytes)
        return compressed

    def decode(self, compressed):
        # Descomprimim
        target_bytes = zlib.decompress(compressed)
        target = target_bytes.decode("ascii")
        decoded = self._ndecoder.decode(target)
        return decoded
