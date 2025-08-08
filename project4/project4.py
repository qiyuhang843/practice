# -*- coding: utf-8 -*-
import math
import hashlib
import random
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

def left_rotate(x, n, w):
    return ((x << n) | (x >> (w - n))) & ((1 << w) - 1)

def sm3(message):
    # 初始化哈希值
    iv = [
        0x7380166f, 0x4914b2b9, 0x172442d7, 0xdaef6e67,
        0x99959129, 0x55659481, 0x5a63d42f, 0xe6913831
    ]
    # 消息分组
    message = bytearray(message, 'utf-8')
    message_bit_len = len(message) * 8
    message += b'\x80'
    while len(message) * 8 % 512 != 448:
        message += b'\x00'
    message += (message_bit_len).to_bytes(8, 'big')
    # 分组处理
    groups = [message[i:i+64] for i in range(0, len(message), 64)]
    for group in groups:
        # 消息扩展
        w = []
        for i in range(16):
            w.append(int.from_bytes(group[i*4:(i+1)*4], 'big'))
        for i in range(16, 68):
            ss1 = left_rotate((w[i-16] ^ w[i-9] ^ left_rotate(w[i-3], 15, 32)), 1, 32)
            ss2 = ss1 ^ left_rotate(w[i-13], 7, 32)
            w.append(ss2 ^ w[i-6])
        # 压缩函数
        a, b, c, d, e, f, g, h = iv
        for i in range(64):
            ss1 = (left_rotate(e, 25, 32) + b + left_rotate((e & f) ^ ((~e) & g), 11, 32) + w[i]) % (2**32)
            ss2 = ss1 ^ left_rotate(e, 2, 32)
            tt = (h + ss2 + (a + left_rotate((a & b) ^ (a & c) ^ (b & c), 15, 32) + w[i+4]) % (2**32)) % (2**32)
            d, c, b, a, h, g, f, e = c, b, a, tt, g, f, e, d
        iv = [
            (iv[0] + a) % (2**32),
            (iv[1] + b) % (2**32),
            (iv[2] + c) % (2**32),
            (iv[3] + d) % (2**32),
            (iv[4] + e) % (2**32),
            (iv[5] + f) % (2**32),
            (iv[6] + g) % (2**32),
            (iv[7] + h) % (2**32)
        ]
    # 生成哈希值
    hash_value = b''
    for part in iv:
        hash_value += part.to_bytes(4, 'big')
    return hash_value.hex()

def length_extension_attack(original_msg, original_hash, extension_msg):
    # 解析原始哈希值
    iv = []
    for i in range(0, len(original_hash), 8):
        iv.append(int(original_hash[i:i+8], 16))
    # 构造新的消息
    new_msg = original_msg + extension_msg
    # 计算填充
    padding = b'\x80'
    while (len(original_msg) + len(padding)) % 64 != 56:
        padding += b'\x00'
    padding += (len(original_msg)*8).to_bytes(8, 'big')
    # 计算新的哈希值
    new_hash = sm3_with_iv(extension_msg, iv)
    return new_msg, new_hash

def sm3_with_iv(message, iv):
    message = bytearray(message, 'utf-8')
    message_bit_len = len(message) * 8
    message += b'\x80'
    while len(message) * 8 % 512 != 448:
        message += b'\x00'
    message += (message_bit_len).to_bytes(8, 'big')
    groups = [message[i:i+64] for i in range(0, len(message), 64)]
    for group in groups:
        w = []
        for i in range(16):
            w.append(int.from_bytes(group[i*4:(i+1)*4], 'big'))
        for i in range(16, 68):
            ss1 = left_rotate((w[i-16] ^ w[i-9] ^ left_rotate(w[i-3], 15, 32)), 1, 32)
            ss2 = ss1 ^ left_rotate(w[i-13], 7, 32)
            w.append(ss2 ^ w[i-6])
        a, b, c, d, e, f, g, h = iv
        for i in range(64):
            ss1 = (left_rotate(e, 25, 32) + b + left_rotate((e & f) ^ ((~e) & g), 11, 32) + w[i]) % (2**32)
            ss2 = ss1 ^ left_rotate(e, 2, 32)
            tt = (h + ss2 + (a + left_rotate((a & b) ^ (a & c) ^ (b & c), 15, 32) + w[i+4]) % (2**32)) % (2**32)
            d, c, b, a, h, g, f, e = c, b, a, tt, g, f, e, d
        iv = [
            (iv[0] + a) % (2**32),
            (iv[1] + b) % (2**32),
            (iv[2] + c) % (2**32),
            (iv[3] + d) % (2**32),
            (iv[4] + e) % (2**32),
            (iv[5] + f) % (2**32),
            (iv[6] + g) % (2**32),
            (iv[7] + h) % (2**32)
        ]
    hash_value = b''
    for part in iv:
        hash_value += part.to_bytes(4, 'big')
    return hash_value.hex()



# 测试
test_message = "hello"
print(f"Message: {test_message}")
print(f"SM3 Hash: {sm3(test_message)}")

original_message = "hello"
original_hash = sm3(original_message)
print(f"Original Message: {original_message}")
print(f"Original Hash: {original_hash}")
extension = " world"
new_message, new_hash = length_extension_attack(original_message, original_hash, extension)
print(f"New Message: {new_message}")
print(f"New Hash: {new_hash}")


def sm3_hash(data):
    return hashlib.new('sm3', data).digest()

class MerkleTree:
    def __init__(self, leaves):
        # 首先对所有的叶子节点进行哈希
        self.leaves = [sm3_hash(leaf) for leaf in leaves]
        self.tree = []
        self.build_tree()

    def build_tree(self):
        current_level = self.leaves.copy()
        self.tree = [current_level]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else current_level[i]
                combined = left + right
                next_level.append(sm3_hash(combined))
            self.tree.append(next_level)
            current_level = next_level

    def get_root(self):
        return self.tree[-1][0] if self.tree else None

    def get_proof(self, index):
        proof = []
        current_index = index
        for level in range(len(self.tree) - 1):
            current_level = self.tree[level]
            if current_index % 2 == 0:
                # 如果是左节点，取右兄弟
                if current_index + 1 < len(current_level):
                    proof.append(('right', current_level[current_index + 1]))
            else:
                # 如果是右节点，取左兄弟
                proof.append(('left', current_level[current_index - 1]))
            current_index = current_index // 2
        return proof

    def verify_proof(self, proof, leaf, root):
        current_hash = sm3_hash(leaf)  # 对输入数据先哈希
        for direction, sibling in proof:
            if direction == 'left':
                combined = sibling + current_hash
            else:
                combined = current_hash + sibling
            current_hash = sm3_hash(combined)
        return current_hash == root

# 测试
# 定义叶子节点数据
leaves = [f"leaf_{i}".encode('utf-8') for i in range(100000)]

# 创建Merkle树
tree = MerkleTree(leaves)
root = tree.get_root()
print(f"Merkle Tree Root Hash: {root.hex()}")

# 验证存在性证明
index = random.randint(0, len(leaves) - 1)
leaf = leaves[index]
proof = tree.get_proof(index)
is_valid = tree.verify_proof(proof, leaf, root)
print(f"Existence proof for leaf_{index}: {is_valid}")

# 验证不存在性证明
non_leaf = f"non_leaf_{random.randint(100000, 200000)}".encode('utf-8')
non_proof = tree.get_proof(index)
non_valid = tree.verify_proof(non_proof, non_leaf, root)
print(f"Non-existence proof for {non_leaf.decode('utf-8')}: {not non_valid}")