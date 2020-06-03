import binascii
import cipher
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from Crypto.Random import get_random_bytes
import zlib
import bz2
import numpy as np

chunks_dict = {
    'IHDR': b'49484452',
    'PLTE': b'504c5445',
    'IDAT': b'49444154',
    'IEND': b'49454e44',
    'tRNS': b'74524e53',
    'cHRM': b'6348524d',
    'gAMA': b'67414d41',
    'iCCP': b'69434350',
    'sBIT': b'73424954',
    'sRGB': b'73524742',
    'tEXt': b'74455874',
    'zTXt': b'7a545874',
    'iTXt': b'69545874',
    'bKGD': b'624b4744',
    'hIST': b'68495354',
    'pHYs': b'70485973',
    'sPLT': b'73504c54',
    'tIME': b'74494d45',
    'eXIf': b'65584966'
}
colour_type_dict = {
    0: "Greyscale",
    2: "Truecolour",
    3: "Indexed-colour",
    4: "Greyscale with alpha",
    6: "Truecolour with alpha"
}
compression_dict = {
    0: "deflate/inflate"
}
filtering_dict = {
    0: "adaptive filtering with five basic filter types"
}
interlace_dict = {
    0: "no interlace",
    1: "Adam7 interlace"
}
bytes_per_pix_dict = {
    0: 1,
    2: 3,
    3: 1,
    4: 2,
    6: 4
}


def ToHex_str(bin):
    return binascii.hexlify(bin)


def ToDec_int(bin):
    return int(binascii.hexlify(bin).decode('ascii'), 16)


class image(object):
    def __init__(self, path):
        self.path = path
        self.colour_palette = []
        self.idat = b''
        self.white_point = None
        self.red_point = None
        self.green_point = None
        self.blue_point = None
        self.default_background_colour = None
        self.time_modification = None
        file = open(path, "rb")
        hex_signature = ToHex_str(file.read(8))
        if hex_signature != b'89504e470d0a1a0a':
            print('not a PNG file')
            file.close()
            exit()

        length = ToDec_int(file.read(4))
        hex = ToHex_str(file.read(4))
        while hex != chunks_dict['IEND']:
            if hex == chunks_dict['IHDR']:
                self.IHDR(file)
            elif hex == chunks_dict['PLTE']:
                self.PLTE(file, length)
            elif hex == chunks_dict['IDAT']:
                self.IDAT(file, length)
            elif hex == chunks_dict['cHRM']:
                self.cHRM(file)
            elif hex == chunks_dict['bKGD']:
                self.bKGD(file)
            elif hex == chunks_dict['tIME']:
                self.tIME(file)
            else:
                file.read(length)
                file.read(4)
            length = ToDec_int(file.read(4))
            hex = ToHex_str(file.read(4))
        file.close()

    def __repr__(self):
        return f"""
        width: {self.width}
        height: {self.height}
        bit depth: {self.bit_depth}
        colour type: {colour_type_dict[self.colour_type]}
        compression method: {compression_dict[self.compression]}
        filtering method: {filtering_dict[self.filtering]}
        interlace method: {interlace_dict[self.interlace]}
        """

    def __str__(self):
        return f"""
        width: {self.width}
        height: {self.height}
        bit depth: {self.bit_depth}
        colour type: {colour_type_dict[self.colour_type]}
        compression method: {compression_dict[self.compression]}
        filtering method: {filtering_dict[self.filtering]}
        interlace method: {interlace_dict[self.interlace]}
        """

    def get_ancillary_data(self):
        return f"""
        cHRM:
        white point: {self.white_point}
        red point:   {self.red_point}
        green point: {self.green_point}
        blue point:  {self.blue_point}

        bKGD:
        {self.get_bKGD()}

        tIME:
        time of last modification: {self.time_modification}
        """

    def IHDR(self, file):
        self.width = ToDec_int(file.read(4))
        self.height = ToDec_int(file.read(4))
        self.bit_depth = ToDec_int(file.read(1))
        self.colour_type = ToDec_int(file.read(1))
        self.compression = ToDec_int(file.read(1))
        self.filtering = ToDec_int(file.read(1))
        self.interlace = ToDec_int(file.read(1))
        self.bytes_per_pix = bytes_per_pix_dict[self.colour_type]
        self.scanline_length = self.width * self.bytes_per_pix + 1
        check_sum = file.read(4)

    def PLTE(self, file, length):
        for _ in range(int(length / 3)):
            self.colour_palette.append((
                ToDec_int(file.read(1)),
                ToDec_int(file.read(1)),
                ToDec_int(file.read(1))))
        file.read(4)

    def IDAT(self, file, length):
        self.idat += ToHex_str(file.read(length))
        file.read(4)

    def cHRM(self, file):
        self.white_point = (ToDec_int(file.read(4)) / 100000, ToDec_int(file.read(4)) / 100000)
        self.red_point = (ToDec_int(file.read(4)) / 100000, ToDec_int(file.read(4)) / 100000)
        self.green_point = (ToDec_int(file.read(4)) / 100000, ToDec_int(file.read(4)) / 100000)
        self.blue_point = (ToDec_int(file.read(4)) / 100000, ToDec_int(file.read(4)) / 100000)
        file.read(4)

    def get_cHRM(self):
        return f"""
        white point: {self.white_point}
        red point:   {self.red_point}
        green point: {self.green_point}
        blue point:  {self.blue_point}
        """

    def bKGD(self, file):
        if self.colour_type == 0 or self.colour_type == 4:
            self.default_background_colour = ToDec_int(file.read(2))
        elif self.colour_type == 2 or self.colour_type == 6:
            self.default_background_colour = (
                ToDec_int(file.read(2)), ToDec_int(file.read(2)), ToDec_int(file.read(2)))  # RGB
        elif self.colour_type == 3:
            self.default_background_colour = ToDec_int(file.read(1))  # index koloru
        file.read(4)

    def get_bKGD(self):
        if self.colour_type == 0 or self.colour_type == 4:
            return f"default background greyscale: {self.default_background_colour}"
        elif self.colour_type == 2 or self.colour_type == 6:
            return f"default background truecolour: {self.default_background_colour}"
        elif self.colour_type == 3:
            return f"default background indexed: {self.default_background_colour}"

    def tIME(self, file):
        year = str(ToDec_int(file.read(2)))
        month = str(ToDec_int(file.read(1)))
        day = str(ToDec_int(file.read(1)))
        hour = str(ToDec_int(file.read(1)))
        minute = str(ToDec_int(file.read(1)))
        second = str(ToDec_int(file.read(1)))
        self.time_modification = day + '.' + month + '.' + year + ' ' + hour + ':' + minute + ':' + second
        file.read(4)

    def getDecompressedIDAT(self):
        return zlib.decompress(binascii.unhexlify(self.idat))

    def getScanlines(self):
        decompressed = self.getDecompressedIDAT()
        scanlines = [decompressed[i * self.scanline_length:(i + 1) * self.scanline_length] for i in
                     range(0, self.height)]
        return scanlines

    def getECBEncryptedIDATandRest(self, rsa):
        scanlines = self.getScanlines()
        pixData = b''
        filterBytes = b''
        for scanline in scanlines:
            pixData += scanline[1:]
            filterBytes += scanline[0:1]
        encrypted_block_rest_pairs = rsa.ecb_encrypt(pixData, self.colour_type)
        encrypted_bytes = b''
        rests = b''
        for pair in encrypted_block_rest_pairs:
           encrypted_bytes += pair[0]
           rests += len(pair[1]).to_bytes(4, 'big') + pair[1]

        encrypted_lst = [encrypted_bytes[i:i + 1] for i in range(0, len(encrypted_bytes))]
        for i in range(len(filterBytes)):
            encrypted_lst.insert(i * self.scanline_length, filterBytes[i:i + 1])
        newIDAT_lst = encrypted_lst[:len(pixData) + len(filterBytes)]
        newIDAT = b''.join(newIDAT_lst)
        compressedIDAT = zlib.compress(newIDAT)
        return compressedIDAT, rests

    def getECBDecryptedIDAT(self, rsa):
        scanlines = self.getScanlines()
        pixData = b''
        filterBytes = b''
        for scanline in scanlines:
            pixData += scanline[1:]
            filterBytes += scanline[0:1]
        pixData_blocks = [pixData[i:i + self.bytes_per_pix] for i in range(0, len(pixData), self.bytes_per_pix)]

        file = open(self.path, "rb")
        temp = file.read()
        file.close()
        rests = temp.split(b'IEND')[1][4:]
        rests_lst = []
        length = ToDec_int(rests[0:4])
        i = 0
        while length != 1413828164: # int(b'TEND')
            rests_lst.append(rests[i+4:i+4+length])
            i = i + 4 + length
            length = ToDec_int(rests[i:i+4])

        encrypted_pairs = []
        for i in range(len(pixData_blocks)):
            encrypted_pairs.append([pixData_blocks[i], rests_lst[i]])

        decrypted_bytes = rsa.ecb_decrypt(encrypted_pairs, self.colour_type)

        decrypted_lst = [decrypted_bytes[i:i + 1] for i in range(0, len(decrypted_bytes))]
        for i in range(len(filterBytes)):
            decrypted_lst.insert(i * self.scanline_length, filterBytes[i:i + 1])
        newIDAT_lst = decrypted_lst[:len(pixData) + len(filterBytes)]
        newIDAT = b''.join(newIDAT_lst)
        compressedIDAT = zlib.compress(newIDAT)
        return compressedIDAT

    def getCBCEncryptedIDATandRest(self, rsa):
        scanlines = self.getScanlines()
        pixData = b''
        filterBytes = b''
        for scanline in scanlines:
            pixData += scanline[1:]
            filterBytes += scanline[0:1]
        encrypted_block_rest_pairs, vector = rsa.cbc_encrypt(pixData, self.colour_type)
        encrypted_bytes = b''
        rests = b''
        for pair in encrypted_block_rest_pairs:
           encrypted_bytes += pair[0]
           rests += len(pair[1]).to_bytes(4, 'big') + pair[1]

        encrypted_lst = [encrypted_bytes[i:i + 1] for i in range(0, len(encrypted_bytes))]
        for i in range(len(filterBytes)):
            encrypted_lst.insert(i * self.scanline_length, filterBytes[i:i + 1])
        newIDAT_lst = encrypted_lst[:len(pixData) + len(filterBytes)]
        newIDAT = b''.join(newIDAT_lst)
        compressedIDAT = zlib.compress(newIDAT)
        return compressedIDAT, rests, vector

    def getCBCDecryptedIDAT(self, rsa, vector):
        scanlines = self.getScanlines()
        pixData = b''
        filterBytes = b''
        for scanline in scanlines:
            pixData += scanline[1:]
            filterBytes += scanline[0:1]
        pixData_blocks = [pixData[i:i + self.bytes_per_pix] for i in range(0, len(pixData), self.bytes_per_pix)]

        file = open(self.path, "rb")
        temp = file.read()
        file.close()
        rests = temp.split(b'IEND')[1][4:]
        rests_lst = []
        length = ToDec_int(rests[0:4])
        i = 0
        while length != 1413828164: # int(b'TEND')
            rests_lst.append(rests[i+4:i+4+length])
            i = i + 4 + length
            length = ToDec_int(rests[i:i+4])

        encrypted_pairs = []
        for i in range(len(pixData_blocks)):
            encrypted_pairs.append([pixData_blocks[i], rests_lst[i]])

        decrypted_bytes = rsa.cbc_decrypt(encrypted_pairs, self.colour_type, vector)

        decrypted_lst = [decrypted_bytes[i:i + 1] for i in range(0, len(decrypted_bytes))]
        for i in range(len(filterBytes)):
            decrypted_lst.insert(i * self.scanline_length, filterBytes[i:i + 1])
        newIDAT_lst = decrypted_lst[:len(pixData) + len(filterBytes)]
        newIDAT = b''.join(newIDAT_lst)
        compressedIDAT = zlib.compress(newIDAT)
        return compressedIDAT

    def saveImageWithIDAT(self, filename, newIDAT, rests):

        file = open(self.path, "rb")
        temp = file.read()
        file.close()
        split = temp.split(b'IDAT')
        newsplit = []
        newsplit.append(split[0][:-4])
        lenght = ToDec_int(split[0][-4:])
        for i in range(1, len(split) - 1):
            newsplit.append(split[i][lenght + 4:-4])
            lenght = ToDec_int(split[i][-4:])
        newsplit.append(split[-1][lenght + 4:])

        newsplit.insert(1, len(newIDAT).to_bytes(4, byteorder='big'))
        newsplit.insert(2, b'\x49\x44\x41\x54')
        newsplit.insert(3, newIDAT)
        newsplit.insert(4, binascii.crc32(newsplit[2] + newsplit[3]).to_bytes(4, byteorder='big'))
        if rests is not None:
            newsplit.append(rests)
            newsplit.append(b'\x54\x45\x4E\x44')

        x = b''.join(newsplit)

        out_file = open(str(filename) + '.png', "wb")
        out_file.write(x)
        out_file.close()
        print("zapisano plik: " + str(filename) + '.png')

if __name__ == '__main__':
    obraz = image('kostki.png')
    rsa = cipher.RSA(32)
    idat, rests, vector = obraz.getCBCEncryptedIDATandRest(rsa)
    obraz.saveImageWithIDAT('test', idat, rests)

    encrypted = image('test.png')
    decryptedIdat = encrypted.getCBCDecryptedIDAT(rsa, vector)
    encrypted.saveImageWithIDAT('odkodowanytest', decryptedIdat, None)

