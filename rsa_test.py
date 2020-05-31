import unittest

from cipher import RSA
import image


class RSATest(unittest.TestCase):
    def test_idat_rsa_ecb(self):
        cls = image.image('kostki.png')
        data = cls.idat
        rsa = RSA()
        public_key, privaye_key, N = rsa.key_generator(key_size=32)
        out = rsa.ecb_encrypt(public_key, N, data)
        dec = rsa.ecb_decrypt(privaye_key, N, out)
        self.assertEqual(dec, data, 'coding or decoding goes wrong')
