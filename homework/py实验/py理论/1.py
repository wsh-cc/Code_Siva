
# 3.1 闰年判断
def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

# 3.2 最大公约数与最小公倍数
def gcd(a: int, b: int) -> int:
    a, b = abs(a), abs(b)
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)

# 3.3 删除字符串中的指定字符
# 法1：
def remove_charl(s: str, c: str) -> str:

    result = []
    for ch in s:
        if ch != c:
            result.append(ch)
    print("方法一：","".join(result))
# 法2：
def remove_char2(s: str, c: str) -> str:

    result = s.replace(c, "")
  
    print("方法二：","".join(result))

if __name__ == "__main__":
    # 3.1
    year = int(input("输入年份: "))
    print("闰年" if is_leap_year(year) else "非闰年")

    # 3.2
    a = int(input("输入第一个整数: "))
    b = int(input("输入第二个整数: "))
    g = gcd(a, b)
    l = lcm(a, b)
    print("最大公约数:", g)
    print("最小公倍数:", l)

    # 3.3
    s = input("输入字符串s: ")
    c = input("输入字符c: ")
    remove_charl(s, c)
    remove_char2(s, c)