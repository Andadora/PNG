import cv2
import numpy as np


class Fourier:
    def show_img_fft(self, filepath):
        img = cv2.imread(filepath, 0)
        f = np.fft.fft2(img)
        shift_f = np.fft.fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(shift_f))
        img_spectrum = np.asanyarray(magnitude_spectrum, dtype=np.uint8)
        cv2.imshow('spectrum', img_spectrum)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return img, shift_f, magnitude_spectrum

    def show_img_inverse_fft(self, img, shift, spectrum):
        shift = np.fft.fftshift(shift)
        img_back = np.fft.ifft2(shift)
        img_back = np.abs(img_back)
        img_back = np.asanyarray(img_back, dtype=np.uint8)
        cv2.imshow('after inverse', img_back)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    f = Fourier()
    img, shift, spec = f.show_img_fft('D:\Programming\python\PNG\indexed.png')
    f.show_img_inverse_fft(img, shift, spec)
