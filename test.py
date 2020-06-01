import binascii

import image
import zlib
from cipher import RSA


def power(x, m, n):
    a = 1
    while m > 0:
        if m % 2 == 1:
            a = (a * x) % n
        x = (x * x) % n
        m //= 2
    return a


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def decrypt(private_key, N, encrypted_data, key_size):
    msg = b''
    blocks = []
    print(f'k/8 = {key_size//8}')
    for d in encrypted_data:
        x = d[0]
        if d[1] is not None:
            x += d[1]
        blockInt = int(x, 16)
        decodedInt = power(blockInt, private_key, N)
        # decodedHex = format(decodedInt, 'x')
        decodedHex = int_to_bytes(decodedInt)
        blocks.append(decodedInt)
        # print(len(x))

        while len(decodedHex) < key_size / 8:
            decodedHex = b'\x00' + decodedHex

        # print(decodedHex)
        msg += decodedHex

    print(f'dec = {blocks[5000:5200]}')
    return msg, blocks


def encrpyt(public_key, N, data, key_size):
    input_size = len(data)
    block_size = key_size // 4
    print(public_key.bit_length())
    output = []
    last = (input_size % block_size)/2
    print(f'last = {last}')
    ints = []
    block = None
    print(data[0:20])
    for i in range(0, len(data), block_size):
        block = data[i:block_size + i]

        blockInt = int(block, 16)
        ints.append(blockInt)

        codedInt = int(power(blockInt, public_key, N))
        codedHex = []
        codedHex.append(format(codedInt, 'x'))
        # codedHex.append(codedInt.to_bytes(((codedInt.bit_length() + 7) // 8),"big").hex())

        # print( )
        if len(codedHex) > len(block):
            print(f'coded is longer {len(codedHex) - len(block)}')
            codedHex = [codedHex[:len(block) + 1], codedHex[len(block) + 1:]]
        else:
            codedHex.append(None)
        while len(codedHex[0]) < len(block):
            codedHex[0] = '0' + codedHex[0]

        output.append(codedHex)

    # print(block)
    print(f'enc = {ints[5000:5200]}')
    return output, ints


cls = image.image('papuga_anon.png')
# data = cls.idat
data_xx = zlib.decompress(cls.idat)
data = image.ToHex_str(data_xx)

rsa = RSA()
key_size = 64
public_key, privaye_key, N = rsa.key_generator(key_size)
output, ints_before_enc = encrpyt(public_key, N, data, key_size)
# print(output[:20])
dec, ints_after_dec = decrypt(privaye_key, N, output, key_size)

# ints_after_dec = list(map(lambda x: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' if x == b'' else x ,ints_after_dec ))
# n = list(filter(lambda x: x != 0, data_xx))
# print(data_xx[:20])
# print(dec[0:20])
dec = dec[:len(dec)]
print(ints_after_dec == ints_before_enc)
print(len(dec), len(data_xx))
print(dec == data_xx)

x = 25000
print(dec[x:x + 1000])
print(data_xx[x:x + 1000])
