import coloredlogs, logging
import client_config
from Crypto.Cipher import AES
import base64

logging.basicConfig(
    level=logging.DEBUG,
)
coloredlogs.install(level='DEBUG', logger=logging.getLogger(__name__), fmt='%(levelname)s %(message)s')

def decrypt(client_id, client_key, iv_text):
    iv_text_list = iv_text.split('#')
    iv = base64.b64decode(iv_text_list[0].encode()) # convert from str to base64 bytes to raw bytes
    cipher_text = iv_text_list[1]
    cipher_text = base64.b64decode(iv_text_list[1].encode())
    logging.debug("iv bytes: {}, ecnrypted text bytes: {}".format(iv, cipher_text))
    
    cipher_key = bytes.fromhex(str(client_config.RAND) + str(client_key))
    logging.debug("cipher_key: {}".format(cipher_key))
    logging.debug("rand: {} key: {}".format(str(client_config.RAND), str(client_key)))
    cipher = AES.new(cipher_key, AES.MODE_CFB, iv=iv)
    plaintext = cipher.decrypt(cipher_text).decode()
    logging.info("Decrypted text: {}".format(plaintext))
    return plaintext