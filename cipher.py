import binascii
import zlib

import Crypto.Util.number as number
import random
import secrets
import cv2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import image


def append_hex(a, b):
    sizeof_b = 0
    while ((b >> sizeof_b) > 0):
        sizeof_b += 1
    sizeof_b += sizeof_b % 4
    return (a << sizeof_b) | b


def xor_cbc_help(a, b):
    xor = [chr(x ^ y) for (x, y) in zip(a, b)]
    t = b''
    for b in xor:
        t += b.encode()
    return t


class RSA:
    def __init__(self, key_size=64):
        self.key_size = key_size
        self.public_key, self.private_key, self.N = self.key_generator(key_size)
        self.block_size = self.key_size // 4

    def power(self, x, m, n):
        a = 1
        while m > 0:
            if m % 2 == 1:
                a = (a * x) % n
            x = (x * x) % n
            m //= 2
        return a

    def int_to_bytes(self, x: int) -> bytes:
        return x.to_bytes((x.bit_length() + 7) // 8, 'big')

    def encrpyt(self, data):
        input_size = len(data)
        bs = self.block_size
        # print(self.public_key.bit_length())
        output = []
        # print(data[0:20])
        # bytes = b''
        for i in range(0, len(data), bs):
            block = data[i:bs + i]
            blockInt = int(block, 16)
            codedInt = int(self.power(blockInt, self.public_key, self.N))
            codedHex = []
            codedHex.append(format(codedInt, 'x'))
            if len(codedHex) > len(block):
                print(f'coded is longer {len(codedHex) - len(block)}')
                codedHex = [codedHex[:len(block)], codedHex[len(block):]]
            else:
                codedHex.append(None)
            while len(codedHex[0]) < len(block):
               codedHex[0] = '0' + codedHex[0]
            output.append(codedHex)
        return output

    def decrypt(self, encrypted_data):
        msg = b''
        for d in encrypted_data:
            x = d[0]
            if d[1] is not None:
                x += d[1]
            blockInt = int(x, 16)
            decodedInt = self.power(blockInt, self.private_key, self.N)
            # decodedHex = format(decodedInt, 'x')
            decodedHex = self.int_to_bytes(decodedInt)
            while len(decodedHex) < self.key_size / 8:
               decodedHex = b'\x00' + decodedHex
            msg += decodedHex
        return msg

    # def cbc_encrypt(self, e, N, input):
    #     self.cbc_block_size = len('{:x}'.format(e)) - 1
    #     input_size = len(input)
    #     upper_bound = input_size - input_size % self.cbc_block_size
    #     self.cbc_vector = secrets.token_bytes(self.cbc_block_size)
    #     vector = copy.deepcopy(self.cbc_vector)
    #     output = []
    #     for i in range(0, upper_bound, self.cbc_block_size):
    #         xor = xor_cbc_help(input[i:self.cbc_block_size + i], vector)
    #         out = self.encryption(e, N, xor)
    #         output.append(out)
    #         vector = out[0]
    #
    #     return output
    #
    # def cbc_decrypt(self, d, N, output: []):
    #     result = b''
    #     vector = copy.copy(self.cbc_vector)
    #     for block in output:
    #         if block[1] is not None:
    #             x = block[0] + block[1]
    #             print('scalony', x)
    #         else:
    #             x = block[0]
    #         before_xor = self.decryption(d, N, x)
    #         xor = xor_cbc_help(before_xor, vector)
    #         result += xor
    #         vector = block[0]
    #
    #     return result
    #
    # def ecb_encrypt(self, e, N, input):
    #     input_size = len(input)
    #     # self.block_size = len('{:x}'.format(e)) - 1
    #     self.block_size = self.key_size // 4 - 1
    #     output = []
    #     upper_bound = input_size - input_size % self.block_size
    #     for i in range(0, upper_bound, self.block_size):
    #         out = self.encryption(e, N, input[i:self.block_size + i])
    #         output.append(out)
    #     if upper_bound < input_size:
    #         output.append(self.encryption(e, N, input[upper_bound:]))
    #     return output
    #
    # def encryption(self, e, N, msg: bytes):
    #     m = int(binascii.hexlify(msg), 16)
    #     cipher_msg = pow(m, e, N)
    #     zakodowana = int_to_bytes(cipher_msg)
    #     if len(msg) < len(zakodowana):
    #         # print(len(msg), len(zakodowana[:len(msg)]))
    #
    #         return zakodowana[:len(msg)], zakodowana[len(msg):]
    #     elif len(msg) > len(zakodowana):
    #         pass
    #     else:
    #         return zakodowana, None
    #
    # def ecb_decrypt(self, d, N, data):
    #     result = b''
    #     for block in data:
    #         x = b''
    #         if block[1] is not None:
    #             x = block[0] + block[1]
    #         else:
    #             x = block[0]
    #         r = self.decryption(d, N, x)
    #         result += r
    #     return result
    #
    # def decryption(self, d, N, cipher):
    #
    #     c = int(binascii.hexlify(cipher), 16)
    #     msg = pow(c, d, N)
    #     m = int_to_bytes(msg)
    #     return m

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


if __name__ == '__main__':
    obraz = image.image('papuga_anon.png')
    rsa = RSA(64)
    decompressed = zlib.decompress(obraz.idat)
    data = image.ToHex_str(decompressed)

    enc = rsa.encrpyt(data)
    print(len(data))
    enc_str = ''
    for i in enc:
        enc_str += i[0]

    print(len(enc_str))
    decrypted = rsa.decrypt(enc)
    print(decompressed == decrypted)
    print(len(decompressed), len(decrypted))
