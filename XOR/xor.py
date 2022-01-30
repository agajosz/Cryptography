import sys
from string import ascii_lowercase
from string import ascii_uppercase as uppercase
from operator import itemgetter
letters = ascii_lowercase

def prepare():
    origFile = open('orig.txt', 'r')
    plainFile = open('plain.txt', 'w+')
    orig = origFile.read()
    text = ''
    seq = []
    for i in range(len(orig)):
        if orig[i].lower() in ascii_lowercase or orig[i] == ' ':
            text += orig[i].lower()
        if (text.__len__()) % 32 == 0:
            seq.append(text+'\n')
            text = ''
    plainFile.writelines(seq)
    plainFile.close()

def encrypt():
    keyFile = open('key.txt', 'r')
    plainFile = open('plain.txt', 'r')
    encryptFile = open('crypto.txt', 'w+')
    plain = plainFile.readlines()
    plainFile.close()
    key = keyFile.read().lower()
    seq = []
    text = ''
    for i in range(len(plain)):
        if plain[i].__len__()>31:
            for j in range(len(key)):
                plainSign = bin(ord(plain[i][j]))[2:].zfill(8)
                keySign = bin(ord(key[j]))[2:].zfill(8)
                y = bin(int(plainSign, 2) ^ int(keySign, 2))[2:].zfill(8)
                text += y + ' '
            seq.append(text+'\n')
            text = ''
    encryptFile.writelines(seq)


def xor(string):
    x = int(string, 2)
    y = int('00100000', 2)
    return x ^ y


def compare(jList, binTable, i):
    if jList.__len__() > 1:
        if binTable[jList[0]][i] == binTable[jList[1]][i] and  binTable[jList[0]][i] ==  binTable[jList[2]][i]:
            return True


def decrypt(table):
    klucz = {}
    for i in range(32):
        counter = 0
        jList = []
        for j in range(len(table)):
            if table[j][i][:3].__contains__('010'):
                counter += 1
                jList.append(j)
        if counter >= int(len(table)/3):
                 klucz[i] = int('00100000', 2)
        elif counter>1 and counter<int(len(table)/3):
                 if compare(jList, table, i):
                     klucz[i] = xor(table[jList[0]][i])
        else:
            klucz[i] = '00000000'
    return klucz

def decrypting(binTable, decryptedBinKey):
    text = ''
    for i in range(len(binTable)):
        for j in range(len(binTable[i])):
            if decryptedBinKey[j] == '00111111':
                text += '?'
            else:
                y = int(binTable[i][j], 2) ^ int(decryptedBinKey[j], 2)
                text += chr(y)
        text+='\n'
    return text
def cryptoanalysis():
    cryptoFile = open('crypto.txt', 'r')
    keyCrypto = open('key-crypto.txt', 'w')
    decryptFile = open('decrypt.txt', 'w')
    crypto = cryptoFile.readlines()
    cryptoFile.close()
    binTable = []
    binar = ''
    for i in range(len(crypto)):
        seq = []
        for j in range(len(crypto[i])):
            if crypto[i][j] != ' ':
                if crypto[i][j] != '\n':
                    binar += crypto[i][j]
            else:
                seq.append(binar)
                binar = ''
        binTable.append(seq)
    klucz = decrypt(binTable)
    decryptedKey = ''
    decryptedKeyBin = []
    for key, value in klucz.items():
        try:
            decryptedKey += str(chr(value))
            decryptedKeyBin.append(bin(value)[2:].zfill(8))
        except:
            decryptedKey += '?'
            decryptedKeyBin.append(bin(ord('?'))[2:].zfill(8))
    print(decryptedKey)
    keyCrypto.write(decryptedKey)
    text = decrypting(binTable, decryptedKeyBin)
    decryptFile.write(text)


def main():
    if sys.argv[1] == '-p':
        prepare()
    elif sys.argv[1] == '-e':
        encrypt()
    elif sys.argv[1] == '-k':
        cryptoanalysis()


main()
