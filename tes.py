import random 

# variable for rsa
p = 7
q = 11
n = p * q
phi_n = (p-1) * (q-1)
pubKeyList = list()

# gcd
def gcd(x, y):
    while(y):
       x, y = y, x % y
    return abs(x)

# list all possible public key
for i in range(2, phi_n):
    if(gcd(i, phi_n)==1):
        pubKeyList.append(i)

# set rsa key for the client
e = random.choice(pubKeyList)   # pubkey
d = 0                           # prkey
while ((d * e) % phi_n != 1):
    d+=1
pubKey = (e, n)
prKey = d

print(f"{e} {d}")