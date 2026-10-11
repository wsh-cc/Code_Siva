import json
#需要修改的文件路径
FILE_NAME = "users.json"


def load_users():
    """
    从json文件加载用户数据
    将json字符串转化为python对象
    """
    try:
        #文件怎么创建的？当第一次运行程序时，users.json文件不存在，此时load_users函数会捕获FileNotFoundError异常，
        #并返回一个空列表。之后，当添加用户时，save_users函数会创建users.json文件并写入用户数据。
        
        with open(FILE_NAME, "r", encoding="utf-8") as f:#with语句可以自动管理资源，确保文件正确关闭,
            # open()
            # file_name表示要打开的文件名，
            # mode表示打开文件的模式，r表示只读，
            # encoding表示文件的编码格式:utf-8是一种常用的编码格式，支持多语言字符包括中文
            return json.load(f)#json.load()函数将json字符串转换为Python对象
    except FileNotFoundError:#不会抛出异常，而是返回一个空列表，
        return []#如果文件不存在，返回空列表


def save_users(users):
    """
    将用户数据保存到json文件，没有对应文件会创建
    py -》json字符串
    """
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        # w 表示写入模式，如果文件不存在会创建，如果文件存在会覆盖
        json.dump(users, f, ensure_ascii=False, indent=4)
        #json.dump()函数将Python对象转换为json字符串并写入文件，
        # ensure_ascii=False表示不使用ascii编码，允许输出非ascii字符，允许输出中文，
        # indent=4表示格式化输出，缩进4个空格