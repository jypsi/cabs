from Crypto.Cipher import AES
import hashlib


def pad(data):
    length = 16 - (len(data) % 16)
    data += chr(length) * length
    return data


def encrypt(plain_text, working_key):
    iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    plain_text = pad(plain_text)
    enc_digest = hashlib.md5()
    enc_digest.update(working_key.encode())
    enc_cipher = AES.new(enc_digest.digest(), AES.MODE_CBC, iv)
    return enc_cipher.encrypt(plain_text).hex()

def decrypt(cipher_text, working_key):
    iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    dec_digest = hashlib.md5()
    dec_digest.update(working_key.encode())
    encrypted_text = bytes.fromhex(cipher_text)
    dec_cipher = AES.new(dec_digest.digest(), AES.MODE_CBC, iv)
    return dec_cipher.decrypt(encrypted_text).decode()
