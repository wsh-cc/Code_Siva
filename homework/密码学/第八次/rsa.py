from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes


def rsa_sign_demo():
    # 生成RSA密钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    message = b"hello digital signature"

    # 私钥签名
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    print("RSA签名结果：", signature.hex())

    # 公钥验签
    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print("RSA验签成功")
    except Exception:
        print("RSA验签失败")


rsa_sign_demo()