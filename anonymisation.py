import image


class Anonymisation:
    def read_needs_stuf(self, filepath):
        file = open(filepath, "rb")
        has_file_all_needed_chuncks = 0
        is_any_IDAT = False
        is_previous_idat = False

        anon_file_data = file.read(8)
        hex_signature = image.ToHex_str(anon_file_data)
        if hex_signature != b'89504e470d0a1a0a':
            print('not a PNG file')
            file.close()
            exit()
        chunk_length = file.read(4)
        chunk_name = file.read(4)
        # HDR MUST BE 1st
        if image.ToHex_str(chunk_name) != image.chunks_dict['IHDR']:
            print("NO HEADER")
            file.close()
            exit(-1)
        # HDR
        anon_file_data = anon_file_data + chunk_length + chunk_name + file.read(17)
        idat = image.chunks_dict['IDAT']
        while True:
            chunk_length = file.read(4)
            chunk_name = file.read(4)
            dec_len = image.ToDec_int(chunk_length)
            hex_name = image.ToHex_str(chunk_name)
            # if needed
            if self.switch_chunck(hex_name):
                if is_previous_idat and hex_name == idat:
                    print("IDAT's r not consecutive")
                    file.close()
                    exit(-2)
                # safety if's
                if (not is_any_IDAT and hex_name == idat) or (hex_name != idat):
                    has_file_all_needed_chuncks += 1

                if hex_name == idat:
                    is_any_IDAT = True

                # end safety if's
                tmp = file.read(dec_len + 4)
                anon_file_data = anon_file_data + chunk_length + chunk_name + tmp
            else:

                file.read(dec_len + 4)
            if hex_name == image.chunks_dict['IEND']:
                break

        if has_file_all_needed_chuncks < 3:
            print('not enough chunks')
            file.close()
            exit(-3)
        file.close()
        return anon_file_data

    def switch_chunck(self, arg):
        switcher = {
            image.chunks_dict['PLTE']: True,
            image.chunks_dict['IDAT']: True,
            image.chunks_dict['IEND']: True
        }
        return switcher.get(arg, False)


def test():
    anon = Anonymisation()
    x = anon.read_needs_stuf('indexed.png')
    out_file = open("nowy.png", "wb")  # open for [w]riting as [b]inary
    out_file.write(x)
    out_file.close()


if __name__ == '__main__':
    test()
