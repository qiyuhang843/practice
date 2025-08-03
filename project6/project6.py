# -*- coding: utf-8 -*-
import hashlib
import random
from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256

# 模拟 P1 的标识符集合
p1_identifiers = ["user1", "user2", "user3", "user4"]
# 模拟 P2 的标识符和相关值的集合
p2_pairs = [("user2", "100"), ("user3", "200"), ("user5", "300")]

# 哈希函数（使用 SHA-256）
def hash_to_curve(data):
    return hashlib.sha256(data.encode()).digest()

# 生成密钥对（使用椭圆曲线加密）
def generate_key_pair():
    private_key = ECC.generate(curve='P-256')
    public_key = private_key.public_key()
    return private_key, public_key

# P1 的处理
def p1_process(identifiers, private_key):
    hashed_values = []
    for id in identifiers:
        hashed_id = hash_to_curve(id)
        # 模拟指数运算
        hashed_values.append(hashed_id)
    return hashed_values

# P2 的处理
def p2_process(received_values, private_key, pairs):
    exponentiated_values = []
    encrypted_values = {}
    for rv in received_values:
        # 模拟指数运算
        exponentiated_values.append(rv)
    for pair in pairs:
        # 模拟加法同态加密）
        encrypted_values[pair[0]] = hash_to_curve(pair[1])
    return exponentiated_values, encrypted_values

# P1 的最终处理
def p1_final_process(received_values, encrypted_sums, private_key, identifiers, pairs):
    intersection_size = 0
    intersection_sum = 0
    # 计算交集大小和求和
    for id in identifiers:
        for pair in pairs:
            if id == pair[0]:
                intersection_size += 1
                intersection_sum += int(pair[1])
    return intersection_size, intersection_sum

# 主函数
def main():
    # 生成 P1 和 P2 的密钥对
    p1_private_key, p1_public_key = generate_key_pair()
    p2_private_key, p2_public_key = generate_key_pair()

    # P1 的处理
    p1_exponentiated_values = p1_process(p1_identifiers, p1_private_key)

    # P2 的处理
    p2_exponentiated_values, p2_encrypted_values = p2_process(p1_exponentiated_values, p2_private_key, p2_pairs)

    # P1 的最终处理
    intersection_size, intersection_sum = p1_final_process(p2_exponentiated_values, p2_encrypted_values, p1_private_key, p1_identifiers, p2_pairs)

    # 输出结果
    print("Intersection Size:", intersection_size)
    print("Intersection Sum:", intersection_sum)

if __name__ == "__main__":
    main()
