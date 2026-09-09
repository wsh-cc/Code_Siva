def F(r, k):
    return ((r ^ k) << 1) & 0xFF


def encrypt_block(x, keys):
    l = (x >> 8) & 0xFF
    r = x & 0xFF

    for k in keys:
        l, r = r, l ^ F(r, k)

    return (l << 8) | r


def decrypt_block(x, keys):
    l = (x >> 8) & 0xFF
    r = x & 0xFF

    for k in keys[::-1]:
        l, r = r ^ F(l, k), l

    return (l << 8) | r


# 简单测试
keys = [1, 2, 3, 4]
p = 0x1234

c = encrypt_block(p, keys)
d = decrypt_block(c, keys)

print(hex(p), hex(c), hex(d))
def F2(x, k):
    return ((x ^ k) << 1) & 0xFF


def encrypt_unbalanced(l, r, keys):
    for k in keys:
        r_low = r & 0xFF
        r_high = (r >> 8) & 0xFF

        new_l = r_low
        new_r_low = l ^ F2(r_low, k)

        r = (r_high << 8) | new_r_low
        l = new_l

    return l, r


def decrypt_unbalanced(l, r, keys):
    for k in keys[::-1]:
        r_low = r & 0xFF
        r_high = (r >> 8) & 0xFF

        new_r_low = l
        new_l = r_low ^ F2(new_r_low, k)

        r = (r_high << 8) | new_r_low
        l = new_l

    return l, r


# 测试
l0, r0 = 0x12, 0x3456

l1, r1 = encrypt_unbalanced(l0, r0, keys)
l2, r2 = decrypt_unbalanced(l1, r1, keys)

print((l0, r0), (l1, r1), (l2, r2))














