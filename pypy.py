seed = 0b1010011101
key = [3, 1, 4, 1, 5]


def lfsr_step(state):
    # 用 x^10 + x^7 + 1，当成 10 位寄存器
    new_bit = ((state >> 9) ^ (state >> 6)) & 1
    out_bit = state & 1
    state = ((state << 1) & 0x3FF) | new_bit
    return state, out_bit


def lfsr_get_bits(start_state, count):
    state = start_state
    bits = ""
    for _ in range(count):
        state, bit = lfsr_step(state)
        bits += str(bit)
    return bits


def lfsr_get_digit(state):
    num = 0
    for _ in range(4):
        state, bit = lfsr_step(state)
        num = (num << 1) | bit
    return state, num % 10


def make_lfsr_code(start_state):
    state = start_state
    code = ""
    for _ in range(6):
        state, digit = lfsr_get_digit(state)
        code += str(digit)
    return state, code


def lfsr_state_cycle(start_state):
    state = start_state
    used = {}
    count = 0

    while state not in used:
        used[state] = count
        state, _ = lfsr_get_digit(state)
        count += 1

    first = used[state]
    return first, count - first


def lfsr_code_cycle(start_state):
    state = start_state
    used = {}
    count = 0

    while True:
        state, code = make_lfsr_code(state)
        if code in used:
            first = used[code]
            return first, count - first
        used[code] = count
        count += 1


def rc4_init(rc4_key):
    s = [0, 1, 2, 3, 4, 5, 6, 7]
    j = 0
    for i in range(8):
        j = (j + s[i] + rc4_key[i % len(rc4_key)]) % 8
        s[i], s[j] = s[j], s[i]
    return s


def rc4_step(s, i, j):
    i = (i + 1) % 8
    j = (j + s[i]) % 8
    s[i], s[j] = s[j], s[i]
    t = (s[i] + s[j]) % 8
    return s[t], i, j


def rc4_stream(rc4_key, count):
    s = rc4_init(rc4_key)
    i = 0
    j = 0
    ans = []

    for _ in range(count):
        value, i, j = rc4_step(s, i, j)
        ans.append(value)

    return ans


def make_rc4_code(rc4_key):
    s = rc4_init(rc4_key)
    i = 0
    j = 0
    code = ""

    for _ in range(6):
        value, i, j = rc4_step(s, i, j)
        code += str(value % 10)

    return code


def rc4_state_cycle(rc4_key):
    s = rc4_init(rc4_key)
    i = 0
    j = 0
    used = {}
    count = 0

    while True:
        state = (tuple(s), i, j)
        if state in used:
            first = used[state]
            return first, count - first
        used[state] = count
        _, i, j = rc4_step(s, i, j)
        count += 1


def rc4_code_cycle(rc4_key):
    s = rc4_init(rc4_key)
    i = 0
    j = 0
    used = {}
    count = 0

    while True:
        code = ""
        for _ in range(6):
            value, i, j = rc4_step(s, i, j)
            code += str(value % 10)
        if code in used:
            first = used[code]
            return first, count - first
        used[code] = count
        count += 1


if __name__ == "__main__":
    print("===== (1) LFSR =====")
    print("寄存器位数: 10")
    print("反馈函数: x^10 + x^7 + 1")
    print("初始值:", format(seed, "010b"))
    print("前20个输出比特:", lfsr_get_bits(seed, 20))
    print()

    print("===== (2) RC4 =====")
    print("数组长度: 8")
    print("密钥:", key)
    print("前20个密钥流:", rc4_stream(key, 20))
    print()

    print("===== (3) 动态验证码 =====")
    _, lfsr_code = make_lfsr_code(seed)
    rc4_code = make_rc4_code(key)
    print("基于LFSR生成6位验证码:", lfsr_code)
    print("基于RC4生成6位验证码:", rc4_code)
    print()

    print("===== 循环测试 =====")
    first1, cycle1 = lfsr_state_cycle(seed)
    first2, cycle2 = rc4_state_cycle(key)
    first3, cycle3 = lfsr_code_cycle(seed)
    first4, cycle4 = rc4_code_cycle(key)

    print("LFSR状态第一次回到旧状态前一共输出:", first1 + cycle1, "次, 周期 =", cycle1)
    print("RC4状态第一次回到旧状态前一共输出:", first2 + cycle2, "次, 周期 =", cycle2)
    print("LFSR验证码生成到第", first3 + cycle3 + 1, "个时开始重复, 循环长度 =", cycle3)
    print("RC4验证码生成到第", first4 + cycle4 + 1, "个时开始重复, 循环长度 =", cycle4)
    