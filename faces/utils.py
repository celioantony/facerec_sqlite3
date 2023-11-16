import numpy as np
import base64

def encode_nparray(nparray):
    """
    Encode type array from numpy to bytes
    """
    sep = base64.b64encode(bytes('|', 'utf-8'))
    arr_dtype = bytes(str(nparray.dtype), 'utf-8')
    encoded = arr_dtype + sep + nparray.tobytes()
    
    return encoded


def decode_nparray(encarray):
    """
    Decode type bytes to array from numpy
    """
    bdtype, encoded = encarray.split(b'fA==')
    dtype = bdtype.decode('utf-8')
    nparray = np.frombuffer(encoded, dtype=dtype)
    
    return nparray
