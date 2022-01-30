from PIL import Image
import hashlib

blockWidth = 4
blockHeight = 3
key = b"Ds1wq&T_xaL9q`nIa8!"

def min(a,b):
    if (a >= b):
        return b
    else:
        return a

def access_bit(data, num):
    base = int(num/8)
    shift = num % 8
    return (data[base] & (1<<shift)) >> shift

def switchKey(b):
    global key
    key = b

def EncryptEBC(a):
    md = hashlib.md5(key)
    md.update(repr(a).encode('utf-8'))
    bytes = md.digest()
    for i in range(0, len(a)):
        a[i] = bytes[i]
        if (i % 15 == 0):
            bytes+=md.digest()

    return a

def EncryptCBC(a):
    md = hashlib.md5(key)
    md.update(repr(a).encode('utf-8'))
    bytes = md.digest()

    for i in range(0, len(a)):
        a[i] = bytes[i]
        if (i % 15 == 0):
            bytes+=md.digest()

    switchKey(repr(a).encode('utf-8'))
    return a


def ProcessBlockEBC(image,x,y,width,height):
    list = [None] * width * height
    k = 0
    for i in range(x,x+width):
        for j in range(y, y+height):
            list[k] = image[i,j]
            k+=1
    a = EncryptEBC(list)
    k = 0
    for i in range(x,x+width):
        for j in range(y, y+height):
            image[i,j] = a[k]
            k+=1

def ProcessBlockCBC(image,x,y,width,height):
    list = [None] * width * height
    k = 0
    for i in range(x,x+width):
        for j in range(y, y+height):
            list[k] = image[i,j]
            k+=1
    a = EncryptCBC(list)
    k = 0
    for i in range(x,x+width):
        for j in range(y, y+height):
            image[i,j] = a[k]
            k+=1

def createBlocks():
    try:
        fkey = open("key.txt","r")
        switchKey(fkey.readline().encode('utf-8'))
    except IOError:
        print ("Plik z kluczem nie istnieje")
        print ("Domyslny klucz: \"Ds1wq&T_xaL9q`nIa8!\"")

    try:
        im1 = Image.open("plain.bmp").convert('L')
    except IOError:
        print ("Plik plain.bmp nie istnieje!")
        return
    width, height = im1.size
    pixels1 = im1.load()
    for x in range(0, width , blockWidth):
        for y in range(0, height ,blockHeight):
            ProcessBlockEBC(pixels1, x, y, min(width - x, blockWidth), min( height - y, blockHeight))

    im1.save("ecb_crypto.bmp")


    im = Image.open("plain.bmp").convert('L')

    pixels = im.load()
    for x in range(0, width , blockWidth):
        for y in range(0, height ,blockHeight):
            ProcessBlockCBC(pixels, x, y, min(width - x, blockWidth), min( height - y, blockHeight))

    im.save("cbc_crypto.bmp")

createBlocks()
