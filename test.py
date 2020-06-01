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


def decrypt(private_key, N, encrypted_data):
    msg = ''
    blocks = []
    for d in encrypted_data:
        x = d[0]
        if d[1] is not None:
            x += d[1]
        blockInt = int(x, 16)
        decodedInt = power(blockInt, private_key, N)
        decodedHex = format(decodedInt, 'x')
        blocks.append(decodedInt)

        msg += decodedHex

    print(f'dec = {blocks[5000:5200]}')
    return msg, blocks


def encrpyt(public_key, N, data, key_size):
    input_size = len(data)
    block_size = key_size // 4
    print(public_key.bit_length())
    output = []
    # upper_bound = input_size - input_size % block_size
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

    print(block)
    print(f'enc = {ints[5000:5200]}')
    return output, ints


cls = image.image('kostki.png')
data = cls.idat
data = zlib.decompress(data)
data = image.ToHex_str(data)

rsa = RSA()
key_size = 32
public_key, privaye_key, N = rsa.key_generator(key_size)
output, ints_before_enc = encrpyt(public_key, N, data, key_size)
# print(output[:20])
dec, ints_after_dec = decrypt(privaye_key, N, output)

# ints_after_dec = list(map(lambda x: b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' if x == b'' else x ,ints_after_dec ))
print(output[0:20])
print(dec[0:20])
print(ints_after_dec == ints_before_enc)
print(len(dec),len(data))
# print(ints_after == ints_before)

# print(ints_before)
# print(ints_after[1000:2000])
