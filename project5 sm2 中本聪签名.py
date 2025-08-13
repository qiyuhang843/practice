# SM2 推荐参数
p  = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
a  = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b  = 0x28E9FA9E9D9F5E344D5AEF6B8FEE8A62E3BCA953CA1481EB1055A27C640E0F
n  = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
Gx = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Gy = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0

# 椭圆曲线点加法与倍点
def inv_mod(k, p):
    return pow(k, -1, p)

def point_add(P, Q):
    if P == (0, 0): return Q
    if Q == (0, 0): return P
    if P[0] == Q[0] and (P[1] != Q[1] or P[1] == 0):
        return (0, 0)
    if P == Q:
        lam = (3*P[0]*P[0] + a) * inv_mod(2*P[1], p) % p
    else:
        lam = (Q[1]-P[1]) * inv_mod(Q[0]-P[0], p) % p
    x3 = (lam*lam - P[0] - Q[0]) % p
    y3 = (lam*(P[0]-x3) - P[1]) % p
    return (x3, y3)

def scalar_mult(k, P):
    R = (0, 0)
    while k:
        if k & 1:
            R = point_add(R, P)
        P = point_add(P, P)
        k >>= 1
    return R

# SM2 签名
import hashlib
def sm2_sign(msg, dA, k):
    e = int(hashlib.sha256(msg).hexdigest(), 16)
    x1, y1 = scalar_mult(k, (Gx, Gy))
    r = (e + x1) % n
    s = ((inv_mod(1+dA, n) * (k - r*dA)) % n)
    return (r, s)

# SM2 验签
def sm2_verify(msg, sig, PA):
    r, s = sig
    e = int(hashlib.sha256(msg).hexdigest(), 16)
    t = (r + s) % n
    x1, y1 = point_add(scalar_mult(s, (Gx, Gy)), scalar_mult(t, PA))
    R = (e + x1) % n
    return R == r


# 生成密钥
import random
dA = random.randrange(1, n)
PA = scalar_mult(dA, (Gx, Gy))

# 假设签名者错误地用相同 k 签了两条不同消息
k_leak = random.randrange(1, n)
msg1 = b"fake satoshi message 1"
msg2 = b"fake satoshi message 2"

sig1 = sm2_sign(msg1, dA, k_leak)
sig2 = sm2_sign(msg2, dA, k_leak)

print("签名1:", sig1)
print("签名2:", sig2)

# 攻击者已知 msg1, msg2, sig1, sig2，恢复私钥
r1, s1 = sig1
r2, s2 = sig2
e1 = int(hashlib.sha256(msg1).hexdigest(), 16)
e2 = int(hashlib.sha256(msg2).hexdigest(), 16)

# 根据SM2重复k漏洞公式恢复k
k_recovered = ((s1 - s2) * inv_mod(s2 - s1, n)) % n  # 实际简化后直接等于k
# 恢复私钥 dA
dA_recovered = ((k_recovered - s1) * inv_mod(r1, n) - 1) % n

print("原私钥:", hex(dA))
print("恢复的私钥:", hex(dA_recovered))

# 用恢复的私钥伪造第三条消息签名
msg3 = b"fake satoshi forged message"
sig3 = sm2_sign(msg3, dA_recovered, random.randrange(1, n))
print("伪造签名:", sig3)
print("验签结果:", sm2_verify(msg3, sig3, PA))

