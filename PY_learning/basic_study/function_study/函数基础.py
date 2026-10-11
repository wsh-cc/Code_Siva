def S_sanjiao(a,b):
    """
    输入三角形的底和高
    输出三角形的面基
    """
    return a*b/2
# print(S_sanjiao(4,3))

def count_yuanying(s):
    """
    输入一个字符串
    输出字符串中的元音字母数量
    """
    count1=0
    for ss in s:
        if ss in "aeiouAEIOU":
            count1+=1
    return count1

def re_score(List):
    """
    输入一个列表
    输出列表中的最高分，最低分，平均分（保留一位小数）
    """
#    print(f"最高分是{max(List):.1f}\n最低分是:{min(List):.1f}\n平均分是:{sum(List)/len(List):.1f}")
    return max(List),min(List),round(sum(List)/len(List),1)

def check_range(score):
    """
    输入一个成绩
    输出级别（A、B、C、D）
    """
    if score>=90:return "A"
    elif score >=75:return "B"
    elif score >=60:return "C"
    else :return "D"

def isreverse(s):
    """
    is reverse??
    """
    return s==s[::-1]

# print(isreverse("hello"))

def transform_time(T):
    """
    将传入的秒数转化为“小时；分钟；秒”的格式
    """
    return T/3600,T/60,T%60

def check_sanjiaoxing(a,b,c):
    """
    判断三角形的类型
    """
    if a+b<=c or a+c<=b :
        print("不构成三角形")
        return "error"
    elif a==b==c :
        return "正三角形"
    elif a==c or b==c or a==b:
        return "等腰三角形"
    else: return "普通三角形"

