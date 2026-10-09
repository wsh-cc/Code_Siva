# 实验五：ECC 基本运算实现

# 椭圆曲线参数：y^2 = x^3 + ax + b (mod p)
p = 19
a = 1
b = 1

# 无穷远点，用 None 表示
O = None


def inverse_mod(k, p):
    """
    求 k 在模 p 下的逆元
    """
    k = k % p
    if k == 0:
        raise ZeroDivisionError("0 没有模逆元")
    return pow(k, -1, p)


def is_on_curve(P):
    """
    判断点 P 是否在椭圆曲线上
    """
    if P is None:
        return True

    x, y = P
    left = (y * y) % p
    right = (x ** 3 + a * x + b) % p

    return left == right


def point_add(P, Q):
    """
    椭圆曲线点加运算
    """
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    # 如果 P 和 Q 关于 x 轴对称，则结果为无穷远点
    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    # P != Q，普通点加
    if P != Q:
        lam = ((y2 - y1) * inverse_mod(x2 - x1, p)) % p
    else:
        # P == Q，倍点运算
        lam = ((3 * x1 * x1 + a) * inverse_mod(2 * y1, p)) % p

    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p

    return (x3, y3)


def scalar_mult(k, P):
    """
    椭圆曲线数乘运算 kP
    使用双倍-相加法
    """
    result = None
    addend = P

    while k > 0:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1

    return result

## 首先验证点 P 是否在曲线上。
# P = (2, 7)
# print("P 是否在曲线上：", is_on_curve(P))

# #点加运算验证
# P = (2, 7)
# R = point_add(P, P)
# print("2P =", R)
# print("2P 是否在曲线上：", is_on_curve(R))

# #多倍点运算验证
# P = (2, 7)
# R2 = scalar_mult(2, P)
# R3 = scalar_mult(3, P)
# print("2P =", R2)
# print("3P =", R3)
# print("3P 是否在曲线上：", is_on_curve(R3))

# #多倍点运算结果验证
# P = (3, 10)
# for k in range(1, 10):
#     R = scalar_mult(k, P)
#     print(str(k) + "P =", R)

def fun_y (x):
    return (x**3 + x + 1) % 19


for x in range(19):
    y2 = fun_y(x)
    for y in range(19):
        if (y * y) % 19 == y2:
            print("点 (", x, ",", y, ") 在曲线上")

            
