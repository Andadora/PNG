import binascii

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
    'tIME': b'74494d45'
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

def ToHex_str(bin):
    return binascii.hexlify(bin)
def ToDec_int(bin):
    return int(binascii.hexlify(bin).decode('ascii'), 16)


class image(object):
    def __init__(self, path):
        self.path = path
        self.colour_palette = []
        self.idat = b''
        file = open(path, "rb")
        hex_signature = binascii.hexlify(file.read(8))
        if hex_signature != b'89504e470d0a1a0a':
            print('not a PNG file')
            file.close()
            exit()

        length = int(binascii.hexlify(file.read(4)).decode('ascii'), 16)
        hex = binascii.hexlify(file.read(4))
        while(hex != chunks_dict['IEND']):
            if hex == chunks_dict['IHDR']:
                self.IHDR(file)
            elif hex == chunks_dict['PLTE']:
                self.PLTE(file, length)
            elif hex == chunks_dict['IDAT']:
                self.IDAT(file, length)
            #elif hex == chunks_dict['gAMA']:
                #print('gAMA')
                #print(binascii.hexlify(file.read(8)))
            else:
                file.read(length)
                file.read(4)
            length = int(binascii.hexlify(file.read(4)).decode('ascii'), 16)
            hex = binascii.hexlify(file.read(4))
        print('IEND')
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

    def IHDR(self, file):
        self.width = int(binascii.hexlify(file.read(4)).decode('ascii'), 16)
        self.height = int(binascii.hexlify(file.read(4)).decode('ascii'), 16)
        self.bit_depth = int(binascii.hexlify(file.read(1)).decode('ascii'), 16)
        self.colour_type = int(binascii.hexlify(file.read(1)).decode('ascii'), 16)
        self.compression = int(binascii.hexlify(file.read(1)).decode('ascii'), 16)
        self.filtering = int(binascii.hexlify(file.read(1)).decode('ascii'), 16)
        self.interlace = int(binascii.hexlify(file.read(1)).decode('ascii'), 16)
        file.read(4)

    def PLTE(self, file, length): #nie ma w testowym
            #print('PLTE:')
            for _ in range(int(length/3)):
                self.colour_palette.append((
                    int(binascii.hexlify(file.read(1)).decode('ascii'), 16),
                    int(binascii.hexlify(file.read(1)).decode('ascii'), 16),
                    int(binascii.hexlify(file.read(1)).decode('ascii'), 16)))
            print(self.colour_palette)
            file.read(4)

    def IDAT(self, file, length):
        #print('IDAT:')
        self.idat += binascii.hexlify(file.read(length))
        file.read(4)

    def tRNS(self, file, length):
        #print('tRNS:')
        #print(binascii.hexlify(file.read(length)))
        file.read(4)


