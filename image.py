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
        print(length)
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
        # print('IEND')
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
        check_sum = file.read(4)

    def PLTE(self, file, length):  # nie ma w testowym
        # print('PLTE:')
        for _ in range(int(length / 3)):
            self.colour_palette.append((
                ToDec_int(file.read(1)),
                ToDec_int(file.read(1)),
                ToDec_int(file.read(1))))
        # print(self.colour_palette)
        file.read(4)

    def IDAT(self, file, length):
        # print('IDAT:')
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
