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


def decrypt(private_key, N, encrypted_data, key_size, pixel):
    msg = b''
    blocks = []
    d = None
    rest = len(encrypted_data) % pixel
    for d in encrypted_data:
        x = d[0]
        # print(d)
        if d[1] is not None:
            x += d[1]
        blockInt = int(x, 16)
        decodedInt = power(blockInt, private_key, N)
        decodedHex = int_to_bytes(decodedInt)
        blocks.append(decodedInt)
        # print(len(x))
        if d is not encrypted_data[-1]:
            while len(decodedHex) < pixel // 2:
                decodedHex = b'\0' + decodedHex
        else:
            while len(decodedHex) < pixel // 2:
                decodedHex = b'\0' + decodedHex

            # print(int_to_bytes(blockInt))
        # print(decodedHex)
        msg += decodedHex
    # print(f'dec = {blocks[5000:5200]}')
    return msg, blocks


def encrpyt(public_key, N, data, pixel):
    input_size = len(data)
    block_size = pixel
    print(public_key.bit_length())
    output = []

    ints = []
    block = None
    for i in range(0, len(data), block_size):
        block = data[i:block_size + i]
        # print(f'block = {block}')
        blockInt = int(block, 16)
        ints.append(blockInt)

        codedInt = int(power(blockInt, public_key, N))
        codedHex = format(codedInt, 'x')
        value_rest = []
        while len(codedHex) < len(block):
            codedHex = '0' + codedHex

        if len(codedHex) > block_size:
            # print(f'coded is longer {len(codedHex[0]) - len(block)}')
            value_rest = [codedHex[:len(block)], codedHex[len(block):]]

            # print(f'codedHex= {codedHex}')
        else:
            value_rest.append(codedHex)
            value_rest.append(None)

        output.append(value_rest)

    # print(f'enc = {ints[5000:5200]}')
    return output, ints


cls = image.image('papuga_anon.png')
pixel = bytes_per_pixel(cls.colour_type)
print(f'color:= {pixel}')

idat = binascii.unhexlify(cls.idat)
data_xx = zlib.decompress(idat)
data = image.ToHex_str(data_xx)

rsa = RSA()
key_size = 4
public_key, privaye_key, N = rsa.key_generator(key_size)
output, ints_before_enc = encrpyt(public_key, N, data, pixel)
# print(output[:20])
sum = ''
for o in output:
    sum += o[0]
sum = binascii.unhexlify(sum)
sum = zlib.compress(sum, 1)
# cls.saveImageWithIDAT('rsa.png', sum)
dec, ints_after_dec = decrypt(privaye_key, N, output, key_size, pixel)
print('dlugosci danych ', len(sum), len(idat))

print(output[:20])
print(ints_after_dec == ints_before_enc)
print(len(dec), len(data_xx))
print(dec[:len(data_xx)] == data_xx)

x = 25000
# print(dec[:-5])
# print(data_xx[:-5])
