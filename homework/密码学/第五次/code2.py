p = 23
a = 1
b = 1

O = None  # 无穷远点

def inv_mod(x, p):
    return pow(x % p, -1, p)

def is_on_curve(P):
    if P is O:
        return True
    x, y = P
    return (y * y - (x**3 + a*x + b)) % p == 0

def add(P, Q):
    if P is O:
        return Q
    if Q is O:
        return P

    x1, y1 = P
    x2, y2 = Q

    # P + (-P) = O
    if x1 == x2 and (y1 + y2) % p == 0:
        return O

    # P = Q，倍点
    if P == Q:
        lam = (3 * x1 * x1 + a) * inv_mod(2 * y1, p) % p
    else:
        lam = (y2 - y1) * inv_mod(x2 - x1, p) % p

    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p

    return (x3, y3)

def mul(k, P):
    R = O
    for _ in range(k):
        R = add(R, P)
    return R

def all_points():
    pts = []
    for x in range(p):
        rhs = (x**3 + a*x + b) % p
        for y in range(p):
            if y*y % p == rhs:
                pts.append((x, y))
    pts.append(O)
    return pts

G = (6, 4)
M = (5, 4)

print("G在曲线上吗:", is_on_curve(G))
print("M在曲线上吗:", is_on_curve(M))

print("2G =", mul(2, G))
print("3G =", mul(3, G))
print("14G =", mul(14, G))

points = all_points()
print("曲线总点数 =", len(points))

# 找 G 的阶
for n in range(1, 100):
    if mul(n, G) is O:
        print("G的阶 =", n)
        break