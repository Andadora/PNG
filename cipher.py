import binascii
import secrets
import zlib

import Crypto.Util.number as number
import random
import image
import copy


class RSA:
    def __init__(self, key_size=64):
        self.key_size = key_size
        self.public_key, self.private_key, self.N = self.key_generator(key_size)
        self.block_size = self.key_size // 4
        self.cbc_ve = None

        # leng of last preapred file

    def xor_bytes(self, a, b):
        return bytes([x ^ y for x, y in zip(a, b)])

    def power(self, x, m, n):
        a = 1
        while m > 0:
            if m % 2 == 1:
                a = (a * x) % n
            x = (x * x) % n
            m //= 2
        return a

    def int_to_bytes(self, x: int, pixel) -> bytes:
        return x.to_bytes(pixel, 'big')

    def bytes_to_int(self, b) -> int:
        return int.from_bytes(b, 'big')

    def cbc_encrypt(self, data, color: int) -> ([], bytes):
        output = []
        pixel = bytes_per_pixel(color)
        vector = secrets.token_bytes(pixel)
        v1 = copy.deepcopy(vector)
        for i in range(0, len(data), pixel):
            x = data[i:i + pixel]
            xor = self.xor_bytes(x, vector)
            msg_int = self.bytes_to_int(xor)
            encrypted_int = self.power(msg_int, self.public_key, self.N)
            try:
                encrypted_bytes = self.int_to_bytes(encrypted_int, len(data[i:i + pixel]))
            except:
                encrypted_bytes = self.int_to_bytes(encrypted_int, self.key_size // 4)
            value = b''
            rest = b''
            value += encrypted_bytes[:pixel]
            rest += encrypted_bytes[pixel:]
            vector = value
            output.append([value, rest])
        return output, v1

    def cbc_decrypt(self, encrypted_data, color, first_vector):
        msg = b''
        vector = first_vector
        for d in encrypted_data:
            encoded_bytes = d[0] + d[1]
            encoded_int = self.bytes_to_int(encoded_bytes)
            decoded_int = self.power(encoded_int, self.private_key, self.N)
            decoded_byte = self.int_to_bytes(decoded_int, len(d[0]))
            xor = self.xor_bytes(decoded_byte[:len(d[0])], vector)
            vector = d[0]
            msg += xor + decoded_byte[len(d[0]):]
        return msg

    def ecb_encrypt(self, data, color: int) -> []:
        """
        RSA with ecb mode

        :param data: data to encrypt as bytes
        :param color: image.image(".. .png").colour_type
        :return: encrypted data as [[value,rest],[..,..]...]]
            value and rest are bytes
        len(data) == Sum of len(values)
        """

        output = []
        pixel = bytes_per_pixel(color)
        print(color)
        for i in range(0, len(data), pixel):
            x = self.bytes_to_int(data[i:i + pixel])
            encrypted_int = self.power(x, self.public_key, self.N)
            try:
                encrypted_bytes = self.int_to_bytes(encrypted_int, len(data[i:i + pixel]))
            except:
                encrypted_bytes = self.int_to_bytes(encrypted_int, self.key_size // 4)
            value = b''
            rest = b''
            value += encrypted_bytes[:pixel]
            rest += encrypted_bytes[pixel:]
            output.append([value, rest])
        return output

    def ecb_decrypt(self, encrypted_data, color):
        """"
            RSA with ecb mode

            return decrypted data as bytes
        """
        msg = b''
        for d in encrypted_data:
            encoded_bytes = d[0] + d[1]
            encoded_int = self.bytes_to_int(encoded_bytes)
            decoded_int = self.power(encoded_int, self.private_key, self.N)
            decoded_byte = self.int_to_bytes(decoded_int, len(d[0]))
            msg += decoded_byte
        return msg

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


def bytes_per_pixel(color_type):
    switcher = {
        0: 1,
        2: 3,
        3: 4,
        4: 2,
        6: 4,
    }
    return switcher.get(color_type, 1)


if __name__ == '__main__':
    obraz = image.image('papuga_anon.png')
    rsa = RSA(64)
    idat = binascii.unhexlify(obraz.idat)
    decompressed = zlib.decompress(idat)
    enc, v1 = rsa.cbc_encrypt(decompressed, obraz.colour_type)
    enc_str = b''
    print(enc[:20])
    for i in enc:
        enc_str += i[0]

    decrypted = rsa.cbc_decrypt(enc, obraz.colour_type, v1)
    print(len(enc_str))

    print(len(decrypted))
    print(len(decompressed))

    print(decrypted == decompressed)
