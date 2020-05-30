import Crypto.Util.number as number
import random
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import binascii


class RSA:
    def encryption(self, e, N, msg):
        cipher_msg: str = ""
        for c in msg:
            m = ord(c)
            cipher_msg += str(pow(m, e, N)) + ' '

        return cipher_msg

    def decryption(self, d, N, cipher):
        msg = ""

        parts = cipher.split()
        for part in parts:
            if part:
                c = int(part)
                msg += chr(pow(c, d, N))

        return msg

    def key_generator(self, key_size=512) -> (int, int, int):
        """"
            generate keys public, private and p*q
        """

        p = number.getPrime(key_size)
        q = number.getPrime(key_size)
        print(f'p = {p}')
        print(f'q = {q}')
        N = p * q
        print(f'N = {N}')
        phi_N = (p - 1) * (q - 1)

        e = None
        while True:
            e = random.randrange(2 ** (key_size - 1), 2 ** key_size)
            if self.__gcd(e, phi_N)[0] == 1:
                break
        if e is None:
            raise Exception('not find public key')

        print(f'e = {e}')
        d = 0
        try:
            d = self.__mod_inv(e, phi_N)
        except Exception as e:
            raise Exception('not find private key')
        print(f'd = {d}')
        return e, d, N

    def __mod_inv(self, a, b):
        """"
            modular inverse
        """
        g, x, y = self.__gcd(a, b)
        if x < 0:
            x += b

        return x

    def __gcd(self, a, b):
        """"
            extended euc alg
        """
        if a == 0:
            return b, 0, 1
        else:
            b_div_a, b_mod_a = divmod(b, a)
            g, x, y = self.__gcd(b_mod_a, a)
            return g, y - b_div_a * x, x

def encodeECB(key, data):
    ctECB_bytes = AES.new(key, AES.MODE_ECB).encrypt(pad(data, AES.block_size)) 
    return  ctECB_bytes

def decodeECB(key, data):
    ptECB = unpad(AES.new(key, AES.MODE_ECB).decrypt(data), AES.block_size)
    return ptECB

def encodeCBC(key, data):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ctCBC_bytes = cipher.encrypt(pad(data, AES.block_size))
    return  ctCBC_bytes, iv

def decodeCBC(key, iv, data):
    ptCBC = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(data), AES.block_size)
    return ptCBC

if __name__ == '__main__':
    data = b'\x53\xad\x23\xb1\x28\x34\xb1\x28\x34'
    print(int(binascii.hexlify(data).decode('ascii'), 16))
    print((int(len(data))).to_bytes(4, byteorder='big'))
    #rsa = RSA()
    #public_key, privaye_key, N = rsa.key_generator(key_size=512)
    #ctRSA = rsa.encryption(public_key, N, data)
    #print(f'RSA encrypted: {ctRSA}')
    #ptRSA = rsa.decryption(privaye_key, N, ctRSA)
    #print(f'RSA decrypted: {ptRSA}')

    key = get_random_bytes(16)

    ctECB = encodeECB(key, data)
    print(f'ECB encrypted: {ctECB}')    
    print((int(len(ctECB))).to_bytes(4, byteorder='big'))
    ptECB = decodeECB(key, ctECB)
    print(f'ECB decrypted: {ptECB}')

    ctCBC, iv = encodeCBC(key, data)
    print(f'CBC encrypted: {ctCBC}')     
    print((int(len(ctCBC))).to_bytes(4, byteorder='big'))
    ptCBC = decodeCBC(key, iv, ctCBC)
    print(f'CBC decrypted: {ptCBC}')