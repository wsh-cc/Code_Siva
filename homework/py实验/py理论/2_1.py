
# strings = []
# for i in range(3):
#     s = input(f"请输入第 {i + 1} 个字符串：")
#     strings.append(s)

# strings.sort(reverse=True)
# print("降序排序结果：", strings)


# strings = []
# for i in range(3):
#     s = input(f"请输入第 {i + 1} 个字符串：")
#     strings.append(s)

# result = sorted(strings, reverse=True)
# print("降序排序结果：", result)


# strings = []
# for i in range(3):
#     s = input(f"请输入第 {i + 1} 个字符串：")
#     strings.append(s)

# # key=str.lower 表示排序时统一按小写形式比较，但输出仍保留原字符串。
# result = sorted(strings, key=str.lower, reverse=True)
# print("忽略大小写后的降序排序结果：", result)


import math


def check_triangle(func):
    """装饰器：检查三角形边长是否合法。"""
    def wrapper(a, b, c):
        if a <= 0 or b <= 0 or c <= 0:
            print("输入错误：三角形边长必须大于 0。")
            return None
        if a + b <= c or a + c <= b or b + c <= a:
            print("输入错误：任意两边之和必须大于第三边。")
            return None
        return func(a, b, c)

    return wrapper

@check_triangle
def triangle_area(a, b, c):
    """使用海伦公式计算三角形面积。"""
    p = (a + b + c) / 2
    area = math.sqrt(p * (p - a) * (p - b) * (p - c))
    print(f"三角形面积为：{area:.2f}")
    return area


if __name__ == "__main__":
    a = float(input("请输入第 1 条边长："))
    b = float(input("请输入第 2 条边长："))
    c = float(input("请输入第 3 条边长："))

    triangle_area(a, b, c)

