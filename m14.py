#!/usr/bin/env python3
# Byte-at-a-time ECB decryption (harder)

from base64 import b64decode
from Crypto.Random.random import getrandbits, randrange
from Crypto.Cipher import AES
from m09 import pkcs7, de_pkcs7
from m11 import detect_ecb
from m12 import blocksize

RANDOM_KEY = bytes(getrandbits(8) for i in range(16))
RANDOM_PREFIX = bytes(getrandbits(8) for i in range(randrange(16)))

def oracle(plaintext = b'', prefix = RANDOM_PREFIX):
    unknown_string = b64decode(open("data/12.txt", "r").read())
    plaintext = pkcs7(prefix + plaintext + unknown_string, 16)
    cypher = AES.new(RANDOM_KEY, AES.MODE_ECB)
    return cypher.encrypt(plaintext)

def decrypt(cyphertext):
    cypher = AES.new(RANDOM_KEY, AES.MODE_ECB)
    return de_pkcs7(cypher.decrypt(cyphertext))

def len_prefix(oracle): # broken when len(prefix) = 0 and >> 0.
    for i in range(32, 48):
        c = oracle(i * b'A')
        if detect_ecb(c): # rewrite without function call?
            offset = (48 - i) % 16
            for b in range(len(c) // 16):
                if c[(b+1)*16:(b+2)*16] == c[(b+2)*16:(b+3)*16]:
                    return 16 * b + offset
            return 0

def len_string(oracle):
    l = len(oracle())
    bs = blocksize(oracle)
    for i in range(1, bs + 1): 
        if l < len(oracle(i * b'A')):
            return l - i - len_prefix(oracle)

def break_ecb(oracle):
    bs = blocksize(oracle)
    l = len(oracle())
    string_length = len_string(oracle)
    prefix_length = len_prefix(oracle)

    plaintext = b''
    uc = (l + bs - len_prefix(oracle) - 1) * b'A'
    while len(plaintext) <= string_length:
        oracle_input = oracle(uc)
        for i in range(127):
            test = uc + plaintext + bytes([i])
            if oracle(test)[l:l + bs] == oracle_input[l:l + bs]:
                uc = uc[1:]
                plaintext += bytes([i])
                #print(chr(i), end = "", flush = True)
                break

    return de_pkcs7(plaintext)

if __name__ == "__main__":
    assert detect_ecb(oracle(48 * b'A')), "Not ECB"

    print(break_ecb(oracle).decode())

