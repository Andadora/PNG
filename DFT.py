import cv2
import numpy as np
from matplotlib import pyplot as plot


class DFT:
    def dft(self, filepath) -> []:
        # wczytanie w sklai szarości
        img = cv2.imread(filepath, 0)

        dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)

        dft_shift = np.fft.fftshift(dft)

        magnitude_spectrum = 20 * np.log((cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1])) + 1)

        cv2.imshow('spectrum',magnitude_spectrum)
        cv2.waitKey(1)
        fig = plot.figure(figsize=(20, 20))
        ax1 = fig.add_subplot(2, 2, 1)
        ax1.imshow(img)
        ax1.title.set_text(str(filepath))
        ax2 = fig.add_subplot(2, 2, 2)
        ax2.imshow(magnitude_spectrum)
        ax2.title.set_text('fft')
        plot.show()


dft = DFT()
dft.dft('D:\Programming\python\PNG\indexed.png')
