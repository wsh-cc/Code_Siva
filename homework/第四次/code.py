from sympy import im


def quick_mode(a, b, n):
    """
    计算 a^b mod n
    """
    result = 1
    a = a % n

    while b > 0:
        if b & 1:
            result = (result * a) % n
        a = (a * a) % n
        b >>= 1

    return result

def extended_gcd(a, b):
    """
    扩展欧几里得算法
    返回 gcd(a,b), x, y
    使得 ax + by = gcd(a,b)
    """
    if b == 0:
        return a, 1, 0

    gcd, x1, y1 = extended_gcd(b, a % b)

    x = y1
    y = x1 - (a // b) * y1

    return gcd, x, y

def inv(a, m):
    """
    求 a 在模 m 下的逆元inv
    """
    gcd, x, y = extended_gcd(a, m)

    if gcd != 1:
        raise ValueError("逆元不存在")

    return x % m

def chinese_remainder(remainders, moduli):
    """
    中国剩余定理
    remainders: 余数列表
    moduli: 模数列表
    """
    M = 1
    for m in moduli:
        M *= m

    result = 0

    for ai, mi in zip(remainders, moduli):
        Mi = M // mi
        ti = inv(Mi, mi)
        result += ai * Mi * ti

    return result % M

import random
def is_probable_prime(n, k=10):
    """
    Miller-Rabin 素性检测
    n: 待检测整数
    k: 检测轮数，轮数越多，判断结果越可靠
    """
    if n < 2:
        return False

    # 先用小素数进行简单筛选，提高效率
    small_primes = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
        31, 37, 41, 43, 47
    ]

    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # 将 n - 1 写成 2^s * d 的形式
    d = n - 1
    s = 0

    while d % 2 == 0:
        s += 1
        d //= 2

    # 进行 k 轮 Miller-Rabin 测试
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = quick_mode(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(s - 1):
            x = quick_mode(x, 2, n)

            if x == n - 1:
                break
        else:
            return False

    return True
def generate_large_prime(bits, k=10):
    """
    生成指定位数的大素数
    bits: 素数的二进制位数
    k: Miller-Rabin 检测轮数
    """
    while True:
        # 随机生成 bits 位整数
        candidate = random.getrandbits(bits)

        # 保证最高位为 1，使其确实是 bits 位数
        candidate |= (1 << bits - 1)

        # 保证最低位为 1，使其为奇数
        candidate |= 1

        if is_probable_prime(candidate, k):
            return candidate

print("一、快速模幂算法验证")
print("9^13 mod 11 =", quick_mode(9, 13, 11))
print("16^7 mod 473 =", quick_mode(16, 7, 473))
print()

print("二、扩展欧几里得算法验证")
gcd, x, y = extended_gcd(17, 3120)
print("gcd(17, 3120) =", gcd)
print("x =", x)
print("y =", y)
print("验证：17*x + 3120*y =", 17 * x + 3120 * y)
print()

print("三、模逆元验证")
d = inv(17, 3120)
print("17 在模 3120 下的逆元 =", d)
print("验证：(17*d) mod 3120 =", (17 * d) % 3120)
print()

print("四、中国剩余定理验证")
remainders = [2, 3, 2]
moduli = [3, 5, 7]
result = chinese_remainder(remainders, moduli)
print("同余方程组的解 x =", result)
print("x mod 3 =", result % 3)
print("x mod 5 =", result % 5)
print("x mod 7 =", result % 7)
print()

print("五、生成大素数")
prime_128 = generate_large_prime(128)

print("生成的 128 位大素数为：")
print(prime_128)
print("二进制位数：", prime_128.bit_length())
print("是否通过 Miller-Rabin 检测：", is_probable_prime(prime_128))