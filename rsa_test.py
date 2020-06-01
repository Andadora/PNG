import unittest
import zlib

from cipher import RSA
import image
import new_rsa


class RSATest(unittest.TestCase):
    def test_idat_rsa_ecb(self):
        cls = image.image('kostki.png')
        data = cls.idat
        data = zlib.decompress(data)
        rsa = RSA()
        key_size = 32
        public_key, privaye_key, N = rsa.key_generator(key_size)
        # out = new_rsa.encrypt(data, public_key, N, key_size)
        print(data[0:20])
        out = rsa.ecb_encrypt(public_key, N, data)
        print(out)
        dec = rsa.ecb_decrypt(privaye_key, N, out)
        print(dec)
        print(dec[0:80] == data[0:80])
        print(len(dec))
        print(len(data))
        # self.assertEqual(len(data), len(dec))
        # self.assertEqual(dec, data, 'coding or decoding goes wrong')

    def test_idat_rsa_cbc(self):
        cls = image.image('kostki.png')
        data = cls.idat
        rsa = RSA()
        public_key, privaye_key, N = rsa.key_generator(key_size=32)
        print(data)
        out = rsa.cbc_encrypt(public_key, N, data)
        print(out)
        r = rsa.cbc_decrypt(privaye_key, N, out)
        print(r)
        self.assertEqual(r, data)
