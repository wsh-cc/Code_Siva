from math import log
from storage import load_users, save_users
from logger import logger
from package.Is_right import checkemail,checkage
import random


# 添加用户
def add_user(name, age, email):
    users = load_users()#程序第一次调用时，会返回一个空列表？

    if not name:
        raise ValueError("姓名不能为空")#如果name为空字符串，抛出ValueError异常，提示姓名不能为空

    if not checkage(age):
        raise ValueError("年龄不合法")
    if not checkemail(email):
        raise ValueError("邮箱不合法")
    user = {
       "id":random.randint(0,10000000),#生成一个随机的用户ID，范围从0到1000000
        "name": name,
        "age": age,
        "email": email
    }

    users.append(user)#
    save_users(users)

    logger.info(f"添加用户: {user}")#
    return user


# 查询全部
def get_users():
    logger.info("用户查询了所有用户")
    return load_users()
   


# 根据ID查询
def get_user_by_id(user_id):
    users = load_users()

    for user in users:
        if user["id"] == user_id:
            return user

    raise ValueError("用户不存在")


# 修改用户
def update_user(user_id, name, age, email):
    users = load_users()

    for user in users:
        if user["id"] == user_id:
            user["name"] = name
            user["age"] = age
            user["email"] = email

            save_users(users)
            logger.info(f"修改用户: {user}")
            return user

    raise ValueError("用户不存在")


# 删除用户
def delete_user(user_id):
    users = load_users()

    for user in users:
        if user["id"] == user_id:
            users.remove(user)
            save_users(users)

            logger.info(f"删除用户: {user}")
            return

    raise ValueError("用户不存在")