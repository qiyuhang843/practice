import math
import hashlib

def rotate_left(x, n):
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

def FF(j, x, y, z):
    if 0 <= j <= 15:
        return x ^ y ^ z
    else:
        return (x & y) | (x & z) | (y & z)

def GG(j, x, y, z):
    if 0 <= j <= 15:
        return x ^ y ^ z
    else:
        return (x & y) | (x & z) | (y & z)

def P0(x):
    return x ^ rotate_left(x, 9) ^ rotate_left(x, 17)

def P1(x):
    return x ^ rotate_left(x, 15) ^ rotate_left(x, 23)

def sm3(data):
    IV = [0x7380166f, 0x4914b2b9, 0x172442d7, 0xdaef6e67,
          0x6704680a, 0x92ca22cd, 0x14292923, 0x0a501ef9]
    data = bytearray(data, 'utf-8')
    data_len = len(data) * 8
    data.append(0x80)
    while len(data) * 8 % 512 != 448:
        data.append(0x00)
    data += data_len.to_bytes(8, 'big')
    for i in range(0, len(data), 64):
        block = data[i:i+64]
        w = [0] * 68
        for j in range(16):
            w[j] = int.from_bytes(block[j*4:j*4+4], 'big')
        for j in range(16, 68):
            w[j] = P1(w[j-16] ^ w[j-8] ^ rotate_left(w[j-3], 15)) ^ rotate_left(w[j-13], 7) ^ w[j-6]
            w[j] &= 0xFFFFFFFF
        a, b, c, d, e, f, g, h = IV
        for j in range(64):
            ss1 = rotate_left(((rotate_left(a, 12) + e) & 0xFFFFFFFF) ^ rotate_left(h, 9), 7)
            ss2 = ss1 ^ rotate_left(a, 12)
            tt1 = (FF(j, a, b, c) + d + ss2 + w[j]) & 0xFFFFFFFF
            tt2 = (GG(j, e, f, g) + h + ss1 + w[j]) & 0xFFFFFFFF
            d, c, b, a = h, g, f, tt1
            g, f, e = e, d, c
            e = (e + tt2) & 0xFFFFFFFF
        IV[0] = (IV[0] + a) & 0xFFFFFFFF
        IV[1] = (IV[1] + b) & 0xFFFFFFFF
        IV[2] = (IV[2] + c) & 0xFFFFFFFF
        IV[3] = (IV[3] + d) & 0xFFFFFFFF
        IV[4] = (IV[4] + e) & 0xFFFFFFFF
        IV[5] = (IV[5] + f) & 0xFFFFFFFF
        IV[6] = (IV[6] + g) & 0xFFFFFFFF
        IV[7] = (IV[7] + h) & 0xFFFFFFFF
    result = b''
    for i in IV:
        result += i.to_bytes(4, 'big')
    return result.hex()

data = "hello"
print("SM3:", sm3(data))
