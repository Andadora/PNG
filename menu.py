from tkinter import filedialog
from tkinter import *

import image
import anonymisation
import fourier
import cipher


def menu():
    print("************MAIN MENU**************")
    rsa = cipher.RSA(64)
    while True:
        choice = input("""
                          A: Wczytaj plik
                          B: Anonimizuj
                          C: FFT
                          D: RSA ECB
                          E: RSA CBC
                          Q: Quit/Log Out
    
                          Please enter your choice: """)

        if choice == "A" or choice == "a":
            root = Tk()
            filepath = filedialog.asksaveasfilename(initialdir="D:\Programming\python\PNG", title="Select file",
                                            filetypes=(("png files", "*.png"), ("all files", "*.*")))
            root.destroy()
            obraz = image.image(filepath)
            print(obraz)
            print(obraz.get_ancillary_data())
            print('idat: ' + str(obraz.idat))
            print('palette: ' + str(obraz.colour_palette))

        elif choice == "B" or choice == "b":
            anonname = input("""
                        Podaj nazwe pliku po anonimizacji bez rozszerzenia
            """)
            anon = anonymisation.Anonymisation()
            anon.save(filepath, anonname)
        elif choice == "C" or choice == "c":
            f = fourier.Fourier()
            img, shift, spec = f.show_img_fft(filepath)
            f.show_img_inverse_fft(img, shift, spec)
        elif choice == "D" or choice == "d":
            obraz = image.image(filepath)
            encrypted_name = input("""
                                                Podaj nazwe pliku po zakodowaniu bez rozszerzenia
                                    """)

            decrypted_name = input("""
                                                Podaj nazwe pliku po odkodowaniu bez rozszerzenia
                                    """)

            idat, rests = obraz.getECBEncryptedIDATandRest(rsa)
            obraz.saveImageWithIDAT(encrypted_name, idat, rests)
            encrypted = image.image(str(encrypted_name) + '.png')
            decryptedIdat = encrypted.getECBDecryptedIDAT(rsa)
            encrypted.saveImageWithIDAT(decrypted_name, decryptedIdat, None)

        elif choice == 'E' or choice == 'e':
            obraz = image.image(filepath)
            encrypted_name = input("""
                                    Podaj nazwe pliku po zakodowaniu bez rozszerzenia
                        """)

            decrypted_name = input("""
                                    Podaj nazwe pliku po odkodowaniu bez rozszerzenia
                        """)
            idat, rests, vector = obraz.getCBCEncryptedIDATandRest(rsa)
            obraz.saveImageWithIDAT(encrypted_name, idat, rests)
            encrypted = image.image(str(encrypted_name) + '.png')
            decryptedIdat = encrypted.getCBCDecryptedIDAT(rsa, vector)
            encrypted.saveImageWithIDAT(decrypted_name, decryptedIdat, None)

        elif choice == "Q" or choice == "q":
            sys.exit()
        else:
            print("You must only select either A,B,C,D,E,Q")
            print("Please try again")
            menu()


if __name__ == '__main__':
    menu()
