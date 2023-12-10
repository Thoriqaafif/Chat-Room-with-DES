# Python program to implement client side of chat room.
import socket
import select
import sys
from math import ceil
from math import log
import time
import random

# convert binary to decimal
def binToDec(bin):
    decimal = 0
    for bit in bin:
        decimal = decimal << 1
        if bit == '1':
            decimal = decimal + 1
    return decimal

# convert decimal to binary
def decToBin(dec, bit):
    num = dec
    bin = str()
    while (num > 0):
        if (num & 1):
            bin = "1" + bin
        else:
            bin = "0" + bin
        num = num >> 1
    length = len(bin)
    bin = "0"*(bit-length) + bin
    return bin

# convert binary to text in ASCII format
def binToText(bin):
    text = str()
    for i in range(len(bin)//8):
        num = binToDec(bin[i*8:i*8+8])
        text = text + str(chr(num))
    return text

# convert text to binary in ASCII format
def textToBin(text):
    bin = str()
    for char in text:
        num = ord(char)
        bin = bin + decToBin(num, 8)
    return bin

# variable for rsa
p = 17
q = 19
n = p * q
phi_n = (p-1) * (q-1)
pubKeyList = list()

# gcd
def gcd(x, y):
    while (y):
        x, y = y, x % y
    return abs(x)


# list all possible public key
for i in range(2, phi_n):
    if (gcd(i, phi_n) == 1):
        pubKeyList.append(i)

# set rsa key for the client
e = random.choice(pubKeyList)   # pubkey
d = 0                           # prkey
while ((d * e) % phi_n != 1):
    d += 1
pubKey = (e, n)
prKey = d

# result for x^y mod p
def modex(x, y, p):
    res = 1

    while(y>0):
        if ((y & 1) != 0):
            res = (res * x)%p
 
        y = y >> 1
        x = x * x 
 
    return res % p

# rsa encryption
def rsa_encrypt(message, pubKey):
    print("Encrypt:")
    pt = message
    ct = str()
    ptList = []
    ctList = []
    blockSize = n
    # print(f"Message = {binToDec(pt)}")

    # for each character
    for char in pt:
        ptNum = ord(char)
        ptList = [ptNum] + ptList
        ctNum = modex(ptNum, pubKey, blockSize)
        ctList = [ctNum] + ctList
        ct = chr(ctNum) + ct

    print("Before encryption:")
    print(f"In decimal: {ptList}")
    print(f"In ascii: {pt}")
    print("After encryption:")
    print(f"In decimal: {ctList}")
    print(f"In ascii: {ct}")

    return ct

# rsa decryption
def rsa_decrypt(message, prKey):
    print("Decrypt:")
    ct = message
    pt = str()
    ptList = []
    ctList = []
    blockSize = n

    # for each character
    for char in ct:
        ctNum = ord(char)
        ctList = [ctNum] + ctList
        ptNum = modex(ctNum, prKey, blockSize)
        ptList = [ptNum] + ptList
        pt = chr(ptNum) + pt
    
    print("Before decryption:")
    print(f"In decimal: {ctList}")
    print(f"In ascii: {ct}")
    print("After decryption:")
    print(f"In decimal: {ptList}")
    print(f"In ascii: {pt}")

    return pt

text = input()
length = len(text)
print(f'Public Key = {pubKey[0]}')
print(f'Private Key = {prKey}')

ct = rsa_encrypt(text, pubKey[0])
print(f"Hasil encrypt dengan rsa = {ct}\n")

pt = rsa_decrypt(ct, prKey)
print(f"Hasil decrypt rsa = {pt}")