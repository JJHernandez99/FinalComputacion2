from cryptography.fernet import Fernet
import os


def encode_image():
    dirpath = os.getcwd()
    imagePath = "imagen.jpeg"
    key = 99
    path = dirpath + '/' + imagePath
    path_result = dirpath + '/' + imagePath + '.enc'
    data = None
    with open(path, 'rb') as f:
        data = f.read()
        f.close()
        size = len(data)
    image = bytearray(data)

    # performing XOR operation on each value of bytearray
    for index, values in enumerate(image):
        image[index] = values ^ key

    # opening file for writing purpose
    fin = open(path_result, 'wb')

    # writing encrypted data in image
    fin.write(image)
    fin.close()
    print('Encryption Done...')


def decode_image():
    dirpath = os.getcwd()
    imagePath = "imagen.jpeg"
    key = 99
    path = dirpath + '/' + imagePath + '.enc'
    path_result = dirpath + '/' + 'result.jpeg'
    # print path of image file and decryption key that we are using
    print('The path of file : ', path)
    print('Note : Encryption key and Decryption key must be same.')
    print('Key for Decryption : ', key)

    # open file for reading purpose
    fin = open(path, 'rb')

    # storing image data in variable "image"
    image = fin.read()
    fin.close()

    # converting image into byte array to perform decryption easily on numeric data
    image = bytearray(image)

    # performing XOR operation on each value of bytearray
    for index, values in enumerate(image):
        image[index] = values ^ key

    # opening file for writing purpose
    fin = open(path_result, 'wb')

    # writing decryption data in image
    fin.write(image)
    fin.close()
    print('Decryption Done...')


if __name__ == '__main__':
    decode_image()
