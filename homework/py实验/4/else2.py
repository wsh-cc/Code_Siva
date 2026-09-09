def sqrt(x):
    """
    求平方根
    """
    if x < 0:
        return "负数不能开平方"
    return x ** 0.5


def pow_num(x, y):
    """
    求 x 的 y 次方
    """
    return x ** y


def factorial(n):
    """
    求阶乘
    """
    if n < 0:
        return "负数没有阶乘"

    result = 1
    for i in range(1, n + 1):
        result *= i

    return result


def fabs(x):
    """
    求绝对值
    """
    if x < 0:
        return -x
    return x