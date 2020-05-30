from tkinter import filedialog
from tkinter import *

import image
import anonymisation
import fourier
import cipher


def menu():
    print("************MAIN MENU**************")
    root = Tk()
    filepath = filedialog.asksaveasfilename(initialdir="D:\Programming\python\PNG", title="Select file",
                                            filetypes=(("png files", "*.png"), ("all files", "*.*")))
    root.destroy()
    while True:
        choice = input("""
                          A: Wczytaj plik
                          B: Anonimizuj
                          C: FFT
                          D: Encrypt ECB
                          Q: Quit/Log Out
    
                          Please enter your choice: """)

        if choice == "A" or choice == "a":
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
        #elif choice == "D" or choice == "d":
        #    encrypted_name = input("""
        #                Podaj nazwe pliku po zakodowaniu bez rozszerzenia
        #    """)
        #    key = get_random_bytes(16)
        #    print(f'klucz: {key}')
        #    obraz =  image.image(filepath)
        #    encryptedIDAT = cipher.encodeECB(key, obraz.IDAT)
        elif choice == "Q" or choice == "q":
            sys.exit()
        else:
            print("You must only select either A,B,C")
            print("Please try again")
            menu()


if __name__ == '__main__':
    menu()
