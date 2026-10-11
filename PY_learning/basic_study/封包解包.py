

# （4）函数不定长参数
def sum_all(*nums):
    """不定长位置参数：求和"""
    return sum(nums)

def info(**kwargs):
    """不定长关键字参数：打印键值"""
    for k, v in kwargs.items():
        print(f"{k} = {v}")

# （5）序列解包与封包
def pack_unpack_demo():
    # 封包：
    packed = 1, "a", 3.14
    print("packed:", packed)

    # 解包：
    x, y, z = packed
    print("unpacked:", x, y, z)

    # 扩展解包
    head, *mid, tail = [10, 20, 30, 40, 50]
    print("head:", head, "mid:", mid, "tail:", tail)

# （6）匿名函数（lambda）
def lambda_demo():
    add = lambda a, b: a + b
    square = lambda x: x * x
    print("add(2, 3) =", add(2, 3))
    print("square(5) =", square(5))

if __name__ == "__main__":


    print("sum_all:", sum_all(1, 2, 3, 4))
    info(name="Alice", age=20, city="Beijing")
    print()

    pack_unpack_demo()
    print()
    
    lambda_demo()

