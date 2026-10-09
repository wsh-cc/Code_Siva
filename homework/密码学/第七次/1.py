import hashlib

def my_hmac_sha256(key, message):
    """
    基于SHA-256实现HMAC
    key：密钥，bytes类型
    message：消息，bytes类型
    """
    block_size = 64   # SHA-256的分组长度是64字节

    # 如果密钥长度大于分组长度，先对密钥做Hash
    if len(key) > block_size:
        key = hashlib.sha256(key).digest()

    # 如果密钥长度不足64字节，用0补齐
    if len(key) < block_size:
        key = key + b'\x00' * (block_size - len(key))

    ipad = bytes([0x36] * block_size)
    opad = bytes([0x5c] * block_size)

    inner_key = bytes([key[i] ^ ipad[i] for i in range(block_size)])
    outer_key = bytes([key[i] ^ opad[i] for i in range(block_size)])

    inner_hash = hashlib.sha256(inner_key + message).digest()
    hmac_result = hashlib.sha256(outer_key + inner_hash).hexdigest()

    return hmac_result


if __name__ == "__main__":
    key = "123456".encode("utf-8")
    message = "这是一段需要认证的消息".encode("utf-8")

    result = my_hmac_sha256(key, message)

    print("密钥：123456")
    print("消息：这是一段需要认证的消息")
print("HMAC-SHA256结果：", result)
