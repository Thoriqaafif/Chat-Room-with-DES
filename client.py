# Python program to implement client side of chat room. 
import socket 
import select 
import sys 
from math import ceil
import time

IP = '192.168.1.13'
Port = 99
key = "AABB09182736CCDD"

# Position table of 64 bits at initial level / initial permutation
initialPermutation = [58, 50, 42, 34, 26, 18, 10, 2,
                      60, 52, 44, 36, 28, 20, 12, 4,
                      62, 54, 46, 38, 30, 22, 14, 6,
                      64, 56, 48, 40, 32, 24, 16, 8,
                      57, 49, 41, 33, 25, 17, 9, 1,
                      59, 51, 43, 35, 27, 19, 11, 3,
                      61, 53, 45, 37, 29, 21, 13, 5,
                      63, 55, 47, 39, 31, 23, 15, 7]

# D-box for exponentiation permutation
dBox = [32, 1, 2, 3, 4, 5,
        4, 5, 6, 7, 8, 9,
        8, 9, 10, 11, 12, 13,
        12, 13, 14, 15, 16, 17,
        16, 17, 18, 19, 20, 21,
        20, 21, 22, 23, 24, 25,
        24, 25, 26 ,27, 28, 29,
        28, 29, 30, 31, 32, 1]

# parity bit table: 64 bits to 56 bits
keyPerm = [57, 49, 41, 33, 25, 17, 9,
           1, 58, 50, 42, 34, 26, 18,
           10, 2, 59, 51, 43, 35, 27,
           19, 11, 3, 60, 52, 44, 36,
           63, 55, 47, 39, 31, 23, 15,
           7, 62, 54, 46, 38, 30, 22,
           14, 6, 61, 53, 45, 37, 29,
           21, 13, 5, 28, 20, 12, 4]

# key compression table: 56 bits to 48 bits
keyComp = [14, 17, 11, 24, 1, 5,
           3, 28, 15, 6, 21, 10,
           23, 19, 12, 4, 26, 8,
           16, 7, 27, 20, 13, 2,
           41, 52, 31, 37, 47, 55,
           30, 40, 51, 45, 33, 48,
           44, 49, 39, 56, 34, 53,
           46, 42, 50, 36, 29, 32]

# S-box table
sbox = [[[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
         [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
         [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
         [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
 
        [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
         [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
         [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
         [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
 
        [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
         [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
         [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
         [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
 
        [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
         [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
         [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
         [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
 
        [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
         [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
         [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
         [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
 
        [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
         [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
         [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
         [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
 
        [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
         [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
         [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
         [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
 
        [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
         [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
         [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
         [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]]

# p-box table
pBox = [16,  7, 20, 21, 29, 12, 28, 17,
        1, 15, 23, 26, 5, 18, 31, 10,
        2,  8, 24, 14, 32, 27,  3,  9,
        19, 13, 30,  6, 22, 11,  4, 25]

# Final Permutation Table
finalPerm = [40, 8, 48, 16, 56, 24, 64, 32,
              39, 7, 47, 15, 55, 23, 63, 31,
              38, 6, 46, 14, 54, 22, 62, 30,
              37, 5, 45, 13, 53, 21, 61, 29,
              36, 4, 44, 12, 52, 20, 60, 28,
              35, 3, 43, 11, 51, 19, 59, 27,
              34, 2, 42, 10, 50, 18, 58, 26,
              33, 1, 41, 9, 49, 17, 57, 25]

# convert hex to binary
def hexToBin(hex):
    mp = {'0': "0000",
          '1': "0001",
          '2': "0010",
          '3': "0011",
          '4': "0100",
          '5': "0101",
          '6': "0110",
          '7': "0111",
          '8': "1000",
          '9': "1001",
          'A': "1010",
          'B': "1011",
          'C': "1100",
          'D': "1101",
          'E': "1110",
          'F': "1111"}
    bin = ""
    for i in range(len(hex)):
        bin = bin + mp[hex[i]]
    return bin

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
    while(num>0):
        if(num&1):
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

# convert binary to hex
def binToHex(bin):
    mp = {"0000": '0',
          "0001": '1',
          "0010": '2',
          "0011": '3',
          "0100": '4',
          "0101": '5',
          "0110": '6',
          "0111": '7',
          "1000": '8',
          "1001": '9',
          "1010": 'A',
          "1011": 'B',
          "1100": 'C',
          "1101": 'D',
          "1110": 'E',
          "1111": 'F'}
    hex = ""
    for i in range(0, len(bin), 4):
        ch = ""
        ch = ch + bin[i]
        ch = ch + bin[i + 1]
        ch = ch + bin[i + 2]
        ch = ch + bin[i + 3]
        hex = hex + mp[ch]
 
    return hex

# shift digit left
def shiftLeft(num, shift, bits):
    result = num << shift
    offset = (result|((1<<bits)-1))>>bits
    result = (result&((1<<bits)-1))|offset
    return result

# do permutation based on given matrix/box
def permute(init, permMatrix):
    permutation = str()
    for i in range(len(permMatrix)):
        permutation = permutation + init[permMatrix[i]-1]
    return permutation

def encrypt(plaintext, key):
    pt = textToBin(plaintext)
    pt_length = len(pt)
    zero_addition = 64-(64%pt_length)
    pt = pt + zero_addition*'0'
    
    kb = hexToBin(key)
    cipherText = str()

    # key permutation: 64 to 56 bits
    kb = permute(kb, keyPerm)
    left = kb[0:28]
    leftDec = binToDec(left)
    right = kb[28:56]
    rightDec = binToDec(right)

    rkb = []    # key in bits for each round
    rkDec = []  # key in decimal for each round

    # generate key in each round
    for i in range(16):
        # for round 1, 2, 9, and 16 key shifted 1
        if i==0 or i==1 or i==8 or i==15:
            shift=1
        # else, key shifted 2
        else:
            shift=2
        
        # shift left and right
        leftDec = shiftLeft(leftDec,shift,28)
        rightDec = shiftLeft(rightDec,shift,28)

        # combine left and right after shift
        combine = (leftDec<<28)|rightDec
        combineBin = decToBin(combine, 56)

        # compression of 56 bits to 48 bits key
        keyRound = permute(combineBin,keyComp)

        rkb.append(keyRound)
        rkDec.append(binToDec(keyRound))

    # encrypt for each block (64 bit / 8 character)
    for i in range(ceil(len(pt)/64)):
        x = i*64
        curr_pt = pt[x:x+64]        # curr plaintext in bin

        # initial permutation
        curr_pt = permute(curr_pt, initialPermutation)

        # split to left and right
        left = curr_pt[0:32]
        right = curr_pt[32:64]

        # process in 16 round
        for j in range(16):
            # Permutation expansion for plaintext, expand 32 bit to 48 bit
            rightExpanded = permute(right, dBox)

            # xor with key
            xorResult = binToDec(rightExpanded)^rkDec[j]
            rightXor = decToBin(xorResult, 48)

            # s-boxes substitution for every 6 bit become 4 bit
            sbox_str = ""
            for k in range(8):
                row = binToDec(rightXor[k*6]+rightXor[k*6+5])
                col = binToDec(rightXor[k*6+1:k*6+5])
                val = sbox[k][row][col]
                valBin = decToBin(val, 4)
                sbox_str = sbox_str + valBin

            # Transposition using p-box
            rightTranspose = permute(sbox_str,pBox)

            # xor with left
            result = binToDec(rightTranspose)^binToDec(left)
            left = right
            right = decToBin(result, 32)
        
        # After 16th round finished, swap left and right then combine
        left, right = right, left
        combine = left + right

        # Final permutation / inverse initial permutation
        cipherText = cipherText + binToText(permute(combine,finalPerm))
        
    return cipherText

def decrypt(ciphertext, key, length):
    ct  = textToBin(ciphertext)
    kb = hexToBin(key)
    plaintext = str()
    
    # key permutation: 64 to 56 bits
    kb = permute(kb, keyPerm)
    left = kb[0:28]
    leftDec = binToDec(left)
    right = kb[28:56]
    rightDec = binToDec(right)

    rkb = []    # key in bits for each round
    rkDec = []  # key in decimal for each round

    # generate key in each round
    for i in range(16):
        # for round 1, 2, 9, and 16 key shifted 1
        if i==0 or i==1 or i==8 or i==15:
            shift=1
        # else, key shifted 2
        else:
            shift=2
        
        # shit left and right
        leftDec = shiftLeft(leftDec,shift,28)
        rightDec = shiftLeft(rightDec,shift,28)

        # combine left and right after shift
        combine = (leftDec<<28)|rightDec
        combineBin = decToBin(combine, 56)

        # compression of 56 bits to 48 bits key
        keyRound = permute(combineBin,keyComp)

        rkb = [keyRound] + rkb
        rkDec = [binToDec(keyRound)] + rkDec

    # encrypt for each block (64 bit / 8 character)
    for i in range(ceil(len(ct)/64)):
        x = i*64
        curr_ct = ct[x:x+64]        # curr plaintext in bin

        # initial permutation
        curr_ct = permute(curr_ct, initialPermutation)

        # split to left and right
        left = curr_ct[0:32]
        right = curr_ct[32:64]

        # process in 16 round
        for j in range(16):
            # Permutation expansion for plaintext, expand 32 bit to 48 bit
            rightExpanded = permute(right, dBox)

            # xor with key
            xorResult = binToDec(rightExpanded)^rkDec[j]
            rightXor = decToBin(xorResult, 48)

            # s-boxes substitution for every 6 bit become 4 bit
            sbox_str = ""
            for k in range(8):
                row = binToDec(rightXor[k*6]+rightXor[k*6+5])
                col = binToDec(rightXor[k*6+1:k*6+5])
                val = sbox[k][row][col]
                valBin = decToBin(val, 4)
                sbox_str = sbox_str + valBin

            # Transposition using p-box
            rightTranspose = permute(sbox_str,pBox)

            # xor with left
            result = binToDec(rightTranspose)^binToDec(left)
            left = right
            right = decToBin(result, 32)
        
        # After 16th round finished, swap left and right then combine
        left, right = right, left
        combine = left + right

        # Final permutation / inverse initial permutation
        plaintext = plaintext + binToText(permute(combine,finalPerm))
        
    return plaintext[:length]
        
if __name__ == "__main__":
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.connect((IP, Port))

	while True:
		sockets_list = [sys.stdin, server]

		read_sockets,write_socket, error_socket = select.select(sockets_list,[],[]) 

		for socks in read_sockets: 
			if socks == server:
				message = socks.recv(2048)
				message = message.decode('utf-8')
				addr, ciphertext, length = message.split(',')
				length = int(length)
                    
				plaintext = decrypt(ciphertext, key, length)
				print(f"Sender: {addr}")
				print(f"Cipher Text: { ciphertext }")
				print(f"message: { plaintext }\n")
				sys.stdout.flush() 
			else: 
				plaintext = input()
				ciphertext = encrypt(plaintext, key)
                    
				message = f"{ciphertext},{len(plaintext)}"
				server.send(message.encode('utf-8'))  
				print(f"Sender: You")
				print(f"message: { plaintext }")
				print(f"Cipher Text: { ciphertext }\n")
				sys.stdout.flush() 
	server.close()