import math

def inv(a, m):
    return pow(a % m, -1, m)

# RSA
print("===== RSA =====")

p, q = 101, 113
n = p * q
phi = (p - 1) * (q - 1)

e = 17
while math.gcd(e, phi) != 1:
    e += 2

d = inv(e, phi)

m = 1234
c = pow(m, e, n)
m2 = pow(c, d, n)

print("p =", p)
print("q =", q)
print("n =", n)
print("phi =", phi)
print("public key =", (e, n))
print("private key =", (d, n))
print("m =", m)
print("c =", c)
print("decrypt =", m2)


#  ElGamal
print("\n===== ElGamal =====")

p, g, a = 11, 2, 5
m, k = 6, 7

beta = pow(g, a, p)

r = pow(g, k, p)
delta = m * pow(beta, k, p) % p
m2 = delta * inv(pow(r, a, p), p) % p

print("p =", p)
print("g =", g)
print("private key =", a)
print("public key =", (p, g, beta))
print("m =", m)
print("c =", (r, delta))
print("decrypt =", m2)


# ECC
print("\n===== ECC =====")

p, A, B = 11, 1, 6
O = None

def neg(P):
    return None if P is None else (P[0], (-P[1]) % p)

def add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if P == Q:
        lam = (3 * x1 * x1 + A) * inv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * inv(x2 - x1, p) % p

    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p

    return x3, y3

def mul(k, P):
    R = None
    while k:
        if k & 1:
            R = add(R, P)
        P = add(P, P)
        k >>= 1
    return R

G = (2, 7)
d = 7
M = (9, 1)
k = 6

PK = mul(d, G)

C1 = mul(k, G)
C2 = add(M, mul(k, PK))

MM = add(C2, neg(mul(d, C1)))

print("curve: y^2 = x^3 + x + 6 mod 11")
print("G =", G)
print("private key =", d)
print("public key =", PK)
print("M =", M)
print("C =", (C1, C2))
print("decrypt =", MM)


