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
        3: 4,
        4: 2,
        6: 4,
    }
    return switcher.get(color_type, "Not found")


def int_to_bytes(x: int, pixel) -> bytes:
    return x.to_bytes(pixel, 'big')


def bytes_to_int(b) -> int:
    return int.from_bytes(b, 'big')


def encrypt_2(public_key, N, data, pixel, key_size):
    output = []

    for i in range(0, len(data), pixel):
        x = bytes_to_int(data[i:i + pixel])
        encrypted_int = power(x, public_key, N)
        try:
            encrypted_bytes = int_to_bytes(encrypted_int, len(data[i:i + pixel]))
        except:
            encrypted_bytes = int_to_bytes(encrypted_int, key_size // 4)
        value = b''
        rest = b''
        value += encrypted_bytes[:pixel]
        rest += encrypted_bytes[pixel:]
        output.append([value, rest])
    return output


def decrypt_2(private_key, N, encrypted_data, key_size, pixel):
    msg = b''
    for d in encrypted_data:
        encoded_bytes = d[0] + d[1]
        encoded_int = bytes_to_int(encoded_bytes)
        decoded_int = power(encoded_int, private_key, N)
        decoded_byte = int_to_bytes(decoded_int, len(d[0]))
        msg += decoded_byte
    return msg


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
            while len(decodedHex) < rest:
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
    return output


cls = image.image('papuga_anon.png')
pixel = bytes_per_pixel(cls.colour_type)
print(f'color:= {pixel}')

idat = binascii.unhexlify(cls.idat)
data_xx = zlib.decompress(idat)

rsa = RSA()
key_size = 32
public_key, privaye_key, N = rsa.key_generator(key_size)
output = encrypt_2(public_key, N, data_xx, cls.colour_type, key_size)
x = 5000
sum = b''
for i in output:
    sum += i[0]
decrypted = decrypt_2(privaye_key, N, output, key_size, pixel)
print(len(sum))
print(len(data_xx))
print(len(decrypted))
print(decrypted == data_xx)
print(output[x:x + 200])


