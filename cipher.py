import sys
from functools import reduce

import Crypto.Util.number as number
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import image


class RSA:

    def ecb_encrypt(self, e, N, input):
        input_size = len(input)
        block_size = 2 * len('{:x}'.format(e))
        #print('{:x}'.format(e)[1])
        #print(input)
        #print(len('{:x}'.format(int(input, 16))), input_size)
        output = []
        upper_bound = input_size - input_size % block_size
        for i in range(0, upper_bound, block_size):
            output.append(self.encryption(e, N, input[i:block_size + i]))

        if upper_bound < input_size:
            output.append(self.encryption(e, N, input[upper_bound:]))
        return output

    def encryption(self, e, N, msg: bytes):
        # print(f'msg = {len(msg)}')
        m = int(msg, 16)

        cipher_msg = pow(m, e, N)
        zakodowana = '{:x}'.format(cipher_msg)
        # print(f'hex = {len(zakodowana)}')
        if len(msg) < len(zakodowana):
            # print(zakodowana[:len(msg)], zakodowana[len(msg):])
            return zakodowana[:len(msg)], zakodowana[len(msg):]
        else:
            return zakodowana, None

    def toHex(self, s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '')
            if len(hv) == 1:
                hv = '0' + hv
            lst.append(hv)

        return reduce(lambda x, y: x + y, lst)

    def decryption(self, d, N, cipher):
        msg = ""

        # parts = cipher.split()
        # for part in parts:
        #     if part:
        c = cipher
        msg = pow(c, d, N)
        m = hex(msg)
        m = '%x' % msg
        print(f'm = {m}')
        m = bytes.fromhex(m).decode('utf-8')

        return m

    def key_generator(self, key_size=512) -> (int, int, int):
        """"
            generate keys public, private and p*q
        """

        p = number.getPrime(key_size)
        q = number.getPrime(key_size)
        # print(f'p = {p}')
        # print(f'q = {q}')
        N = p * q
        # print(f'N = {N}')
        phi_N = (p - 1) * (q - 1)

        e = None
        while True:
            e = random.randrange(2 ** (key_size - 1), 2 ** key_size)
            if self.__gcd(e, phi_N)[0] == 1:
                break
        if e is None:
            raise Exception('not find public key')

        # print(f'e = {e}')
        d = 0
        try:
            d = self.__mod_inv(e, phi_N)
        except Exception as e:
            raise Exception('not find private key')
        # print(f'd = {d}')
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
    return ctECB_bytes


def decodeECB(key, data):
    ptECB = unpad(AES.new(key, AES.MODE_ECB).decrypt(data), AES.block_size)
    return ptECB


def encodeCBC(key, data):
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ctCBC_bytes = cipher.encrypt(pad(data, AES.block_size))
    return ctCBC_bytes, iv


def decodeCBC(key, iv, data):
    ptCBC = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(data), AES.block_size)
    return ptCBC


if __name__ == '__main__':
    data = b'\x53\xad\x23\xb1\x28\x34\xb1\x28\x34'
    # print(int(binascii.hexlify(data).decode('ascii'), 16))
    # print((int(len(data))).to_bytes(4, byteorder='big'))
    rsa = RSA()
    public_key, privaye_key, N = rsa.key_generator(key_size=512)
    obraz = image.image('papagaj.png')
    # print(obraz.idat)
    out = rsa.ecb_encrypt(public_key, N, obraz.idat)
    print(out)