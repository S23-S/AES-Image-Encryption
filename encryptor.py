from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad

KEY = get_random_bytes(16)  # AES-128


def encrypt_ecb(data):
    cipher = AES.new(KEY, AES.MODE_ECB)
    return cipher.encrypt(pad(data, 16))


def encrypt_cbc(data):
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(data, 16))


def encrypt_ctr(data):
    cipher = AES.new(KEY, AES.MODE_CTR)
    return cipher.encrypt(data)