from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import hashes


def create_dsa_keys():
    """生成DSA公钥和私钥"""
    private_key = dsa.generate_private_key(
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key


def dsa_sign(private_key, message):
    """使用DSA私钥进行签名"""
    signature = private_key.sign(
        message,
        hashes.SHA256()
    )
    return signature


def dsa_verify(public_key, message, signature):
    """使用DSA公钥进行验签"""
    try:
        public_key.verify(
            signature,
            message,
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def dsa_demo():
    message = b"hello dsa signature"

    private_key, public_key = create_dsa_keys()

    signature = dsa_sign(private_key, message)

    print("DSS/DSA签名结果：")
    print(signature.hex())

    if dsa_verify(public_key, message, signature):
        print("DSS/DSA验签成功")
    else:
        print("DSS/DSA验签失败")


dsa_demo()