"""
encryption.py
author: Tim Tersigni

- Contains server's encryption function for sending encrypted messages.
"""

import coloredlogs, logging
from Crypto.Cipher import AES
import base64


logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')

def encrypt(rand, key, text: str):
    cipher_key = bytes.fromhex(str(rand) + str(key)) # create cypher key from rand and k_a
    cipher = AES.new(cipher_key, AES.MODE_CFB)
    cipher_text = cipher.encrypt(text.encode())
    cipher_iv_text = base64.b64encode(cipher.iv) + b'#' + base64.b64encode(cipher_text) # convert from raw bytes output to base64 (allows # deliminator) to str for clean output
    cipher_iv_text = cipher_iv_text.decode()
    logging.info("Decrypted text: {}".format(text))
    return cipher_iv_text