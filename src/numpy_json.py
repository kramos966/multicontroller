import socket
import numpy as np
import json
import sys
from base64 import b64encode, b64decode

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        # Comprovem que l'objecte pertanyi a ndarray
        if isinstance(obj, np.ndarray):
            # Creem un diccionari que mapegi l'array a un diccionari
            dic_obj = {}
            dic_obj["shape"] = obj.shape
            dic_obj["dtype"] = str(obj.dtype)
            # Codifico les dades a un string Latin-1, ja que mapeja cada byte indiv. a un símbol
            dic_obj["data"] = b64encode(obj.tobytes()).decode("ascii")
            dic_obj["endianness"] = sys.byteorder
            dic_obj["msg_kind"] = "array"
            return dic_obj
        # En cas que no sigui ndarray, deixem que la classe mare s'encarregui de l'error
        return json.JSONEncoder.default(self, obj) 

class NumpyDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
        self.req_keys = ("shape", "dtype", "data", "endianness", "msg_kind")

    def object_hook(self, dct):
        # Comprovem que hi hagi totes les claus necessàries...
        if all(key in self.req_keys for key in dct.keys()):
            shape = dct["shape"]
            dtype = dct["dtype"]
            data = b64decode(dct["data"])
            endianness = dct["endianness"]
            lin_array = np.frombuffer(data, dtype=dtype)
            # Copiem les dades del búfer a un nou array per modificar-lo.
            # IMPORTANT: Això és necessàri per a modificar-ne l'endianness!
            array = np.array(lin_array.reshape(shape))
            # Modifiquem l'ordre si l'ordre no és el del sistema...
            if endianness != sys.byteorder:
                array.byteswap(inplace=True)
            # Decodifiquem les dades!
            dct["data"] = array
            return dct
        return dct

if __name__ == "__main__":
    def test():
        import zlib
        n = 1024
        a = np.random.rand(n, n)
        b = np.random.rand(n, n)
        z = a+1j*b
        # Codificador i decodificador
        encoder = NumpyEncoder()
        decoder = NumpyDecoder()

        # Codifiquem i decodifiquem!
        print("Encoding...")
        encoded = encoder.encode(z)
        compressed = zlib.compress(encoded.encode("ascii"))
        print()
        print(f"Inflation: {len(compressed)/(8*n*n):.3g}")
        print("Decoding..")
        decoded = decoder.decode(encoded)
        array = decoded["data"]

        # Comprovem que el resultat sigui idèntic
        print("Success?", np.allclose(z, array))

    def test_normal_dict():
        print("Testing encoding a normal dict")
        a = {"message": "Eiii", "msg_kind":"message"}
        print(f"Input: {a}")
        encoder = NumpyEncoder()
        decoder = NumpyDecoder()

        encoded = encoder.encode(a)
        decoded = decoder.decode(encoded)

        print(f"Output: {decoded}")

    test()
    print("------------")
    test_normal_dict()
