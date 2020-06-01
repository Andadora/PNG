import binascii
import zlib

import Crypto.Util.number as number
import random
import secrets
import cv2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import copy
import image


def append_hex(a, b):
    sizeof_b = 0

    # get size of b in bits
    while ((b >> sizeof_b) > 0):
        sizeof_b += 1

    # align answer to nearest 4 bits (hex digit)
    sizeof_b += sizeof_b % 4

    return (a << sizeof_b) | b


def xor_cbc_help(a, b):
    xor = [chr(x ^ y) for (x, y) in zip(a, b)]
    t = b''
    for b in xor:
        t += b.encode()
    return t


class RSA:
    def cbc_encrypt(self, e, N, input):
        self.cbc_block_size = len('{:x}'.format(e)) - 1
        input_size = len(input)
        upper_bound = input_size - input_size % self.cbc_block_size
        self.cbc_vector = secrets.token_bytes(self.cbc_block_size)
        vector = copy.deepcopy(self.cbc_vector)
        output = []
        for i in range(0, upper_bound, self.cbc_block_size):
            xor = xor_cbc_help(input[i:self.cbc_block_size + i], vector)
            out = self.encryption(e, N, xor)
            output.append(out)
            vector = out[0]

        return output

    def cbc_decrypt(self, d, N, output: []):
        result = b''
        vector = copy.copy(self.cbc_vector)
        for block in output:
            if block[1] is not None:
                x = block[0] + block[1]
                print('scalony', x)
            else:
                x = block[0]
            before_xor = self.decryption(d, N, x)
            xor = xor_cbc_help(before_xor, vector)
            result += xor
            vector = block[0]

        return result

    def ecb_encrypt(self, e, N, input):
        input_size = len(input)
        # self.block_size = len('{:x}'.format(e)) - 1
        self.block_size = self.key_size // 4 - 1
        output = []
        upper_bound = input_size - input_size % self.block_size
        for i in range(0, upper_bound, self.block_size):
            out = self.encryption(e, N, input[i:self.block_size + i])
            output.append(out)
        if upper_bound < input_size:
            output.append(self.encryption(e, N, input[upper_bound:]))
        return output

    def encryption(self, e, N, msg: bytes):
        m = int(binascii.hexlify(msg), 16)
        cipher_msg = pow(m, e, N)
        zakodowana = int_to_bytes(cipher_msg)
        if len(msg) < len(zakodowana):
            # print(len(msg), len(zakodowana[:len(msg)]))

            return zakodowana[:len(msg)], zakodowana[len(msg):]
        elif len(msg) > len(zakodowana):
            pass
        else:
            return zakodowana, None

    #def rsa_just_encrypt(self, e, N, value):

    # def toHex(self, s):
    #     lst = []
    #     for ch in s:
    #         hv = hex(ord(ch)).replace('0x', '')
    #         if len(hv) == 1:
    #             hv = '0' + hv
    #         lst.append(hv)
    #
    #     return reduce(lambda x, y: x + y, lst)
    def ecb_decrypt(self, d, N, data):
        result = b''
        for block in data:
            x = b''
            if block[1] is not None:
                x = block[0] + block[1]
            else:
                x = block[0]
            r = self.decryption(d, N, x)
            result += r
        return result

    def decryption(self, d, N, cipher):

        c = int(binascii.hexlify(cipher), 16)
        msg = pow(c, d, N)
        m = int_to_bytes(msg)
        return m

    def key_generator(self, key_size=512) -> (int, int, int):
        """"
            generate keys public, private and p*q
        """
        self.key_size = key_size
        p = number.getPrime(key_size)
        q = number.getPrime(key_size)
        N = p * q
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


def bytes_per_pixel(color_type):
    switcher = {
        0: 1,
        2: 3,
        3: 1,
        4: 2,
        6: 4,
    }
    return switcher.get(color_type, "Not found")


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


if __name__ == '__main__':
    data = b'\x53\xad\x23\xb1\x28\x34\xb1\x28\x34'
    x = int(binascii.hexlify(data), 16)
    print(x)

    obraz = image.image('kostki.png')
    rsa = RSA()
    public_key, privaye_key, N = rsa.key_generator(key_size=32)
    decompressed = zlib.decompress(obraz.idat)
    print('before', len(decompressed))
    enc = rsa.ecb_encrypt(public_key, N, decompressed)
    idat = b''
    for i in enc:
        idat += i[0]
    idat = zlib.compress(idat, 9)
    # print(idat)
    print(f'len of idat {len(idat)}')
    print(idat)
    obraz.saveImageWithIDAT('nowy_rsa', idat)
    encrypted = cv2.imread('papuga_rsa_u_gory.png')
    cv2.imshow('rsa', encrypted)
    cv2.waitKey()
    cv2.destroyAllWindows()
