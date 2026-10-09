from gmssl import sm2, func

def create_sm2_keys():
    """生成一组配套的SM2私钥和公钥"""

    # 私钥：64位十六进制字符串
    private_key = func.random_hex(64)

    # 临时SM2对象，用来根据私钥计算公钥
    temp_sm2 = sm2.CryptSM2(
        public_key="",
        private_key=private_key
    )

    # 公钥 = 私钥 × G
    public_key = temp_sm2._kg(
        int(private_key, 16),
        sm2.default_ecc_table["g"]
    )

    return private_key, public_key


def sm2_sign(private_key, public_key, message):
    """SM2签名"""

    sm2_object = sm2.CryptSM2(
        public_key=public_key,
        private_key=private_key
    )

    random_num = func.random_hex(sm2_object.para_len)

    signature = sm2_object.sign(message, random_num)

    return signature


def sm2_verify(public_key, message, signature):
    """SM2验签"""

    sm2_object = sm2.CryptSM2(
        public_key=public_key,
        private_key=""
    )

    return sm2_object.verify(signature, message)


def sm2_demo():
    message = b"hello sm2 signature"

    private_key, public_key = create_sm2_keys()

    signature = sm2_sign(private_key, public_key, message)

    print("SM2私钥：")
    print(private_key)

    print("SM2公钥：")
    print(public_key)

    print("SM2签名结果：")
    print(signature)

    result = sm2_verify(public_key, message, signature)

    if result:
        print("SM2验签成功")
    else:
        print("SM2验签失败")


sm2_demo()