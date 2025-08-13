import os
from hashlib import sha256

# SM2 参数
p  = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
a  = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b  = 0x28E9FA9E9D9F5E344D5AEF6B8FEE8A62E3BCA953CA1481EB1055A27C640E0F
n  = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0

def mod_inv(x, p):
    return pow(x, p-2, p)

def point_add(P, Q):
    if P == (None, None): return Q
    if Q == (None, None): return P
    if P[0] == Q[0] and (P[1] != Q[1] or P[1] == 0):
        return (None, None)
    if P != Q:
        lam = ((Q[1] - P[1]) * mod_inv(Q[0] - P[0], p)) % p
    else:
        lam = ((3 * P[0] * P[0] + a) * mod_inv(2 * P[1], p)) % p
    x3 = (lam * lam - P[0] - Q[0]) % p
    y3 = (lam * (P[0] - x3) - P[1]) % p
    return (x3, y3)

def scalar_mult(k, P):
    R = (None, None)
    while k:
        if k & 1:
            R = point_add(R, P)
        P = point_add(P, P)
        k >>= 1
    return R

# 密钥生成
def gen_keypair():
    d = int.from_bytes(os.urandom(32), 'big') % n
    P = scalar_mult(d, (Gx, Gy))
    return d, P

# 签名/验签
def sign(msg, d):
    e = int.from_bytes(sha256(msg).digest(), 'big')
    while True:
        k = int.from_bytes(os.urandom(32), 'big') % n
        x1, _ = scalar_mult(k, (Gx, Gy))
        r = (e + x1) % n
        if r == 0 or r + k == n:
            continue
        s = (mod_inv(1 + d, n) * (k - r * d)) % n
        if s != 0:
            return r, s

def verify(msg, sig, P):
    r, s = sig
    e = int.from_bytes(sha256(msg).digest(), 'big')
    t = (r + s) % n
    if t == 0: return False
    x1y1 = point_add(scalar_mult(s, (Gx, Gy)), scalar_mult(t, P))
    x1 = x1y1[0]
    R = (e + x1) % n
    return R == r

if __name__ == "__main__":
    d, P = gen_keypair()
    msg = b"SM2 test"
    sig = sign(msg, d)
    print("Sign:", sig)
    print("Verify:", verify(msg, sig, P))
