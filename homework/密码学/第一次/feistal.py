def rol(x, r, bits):
    mask = (1 << bits) - 1
    r %= bits
    return ((x << r) | (x >> (bits - r))) & mask

#平衡Feistel轮函数 
def F16(right, subkey):
    """16位 -> 16位"""
    return rol((right ^ subkey) & 0xFFFF, 3, 16)

#平衡Feistel加密/解密函数
def feistel_balance(block, key, rounds=16, mode="encode"):
    """
    mode:
      - "encode" 加密
      - "decode" 解密
    """
    L = (block >> 16) & 0xFFFF
    R = block & 0xFFFF

    if mode not in ("encode", "decode"):
        raise ValueError("mode 只能是 'encode' 或 'decode'")

    key_range = range(rounds) if mode == "encode" else range(rounds - 1, -1, -1)

    for i in key_range:
        subkey = (key * (i + 1)) & 0xFFFF
        if mode == "encode":
            L, R = R, (L ^ F16(R, subkey)) & 0xFFFF
        else:
            L, R = (R ^ F16(L, subkey)) & 0xFFFF, L

    return ((L & 0xFFFF) << 16) | (R & 0xFFFF)

#非平衡Feistel 12/20轮函数
MASK_L = 0xFFF      # 12=3*4
MASK_R = 0xFFFFF    # 20=4*5
def F12_to20(l, subkey):#子密钥subkey
    """12位 -> 20位"""
    x = (l ^ (subkey & MASK_L)) & MASK_L
    # 简单扩展混合
    return ((x << 8) | ((x * 0x9E37) & 0xFF)) & MASK_R
def F20_to12(r, subkey):
    """20位 -> 12位"""
    x = (r ^ (subkey & MASK_R)) & MASK_R
    return (x ^ (x >> 7) ^ (x >> 13)) & MASK_L

#非平衡Feistel加密/解密函数
def feistel_unbalance(block, key, rounds=16, mode="encode"):
    L = (block >> 20) & MASK_L
    R = block & MASK_R
    key_range = range(rounds) if mode == "encode" else range(rounds - 1, -1, -1)

    for i in key_range:
        subkey = (key * (i + 1)) & MASK_R
        if mode == "encode":
            R = (R ^ F12_to20(L, subkey)) & MASK_R
            L = (L ^ F20_to12(R, subkey)) & MASK_L
        else:
            L = (L ^ F20_to12(R, subkey)) & MASK_L
            R = (R ^ F12_to20(L, subkey)) & MASK_R

    return ((L & MASK_L) << 20) | (R & MASK_R)

if __name__ == '__main__':
    #八位十六进制数
    public_key= 0x1234567e
    private_key= 0x874443ee

    print(" 平衡 Feistel ")
    Ecoding_text1 = feistel_balance(public_key, private_key, mode="encode")
    Decoding_text1 = feistel_balance(Ecoding_text1, private_key, mode="decode")

    print(f"明文: {hex(public_key)}")
    print(f"密文: {hex(Ecoding_text1)}")
    print(f"解密: {hex(Decoding_text1)}")
    print(f"可逆验证: {'成功' if Decoding_text1 == public_key else '失败'}\n")

    print(" 非平衡 Feistel ")
    Ecoding_text2 = feistel_unbalance(public_key, private_key, mode="encode")
    Decoding_text2 = feistel_unbalance(Ecoding_text2, private_key, mode="decode")

    print(f"明文: {hex(public_key)}")
    print(f"密文: {hex(Ecoding_text2)}")
    print(f"解密: {hex(Decoding_text2)}")
    print(f"可逆验证: {'成功' if Decoding_text2 == public_key else '失败'}")