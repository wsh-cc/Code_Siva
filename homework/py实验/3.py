# # 1. 字典基本操作
# print("\n=== 1. 字典基本操作 ===")
# # 创建字典并访问元素
# info = {'Name': 'Zara', 'Age': 7, 'Class': 'First'}

# print(info['Name'])
# print(info['Age'])

# # 修改和添加元素
# info['Age'] = 8
# info['School'] = 'DPS School'

# print(info)

# # 删除元素、清空字典
# del info['Name']
# print(info)

# info.clear()
# print(info)


# # 2. 字典遍历
# print("\n=== 2. 字典遍历 ===")
# person = {
#     "姓名": "李时珍",
#     "出生时间": 1518,
#     "籍贯": "湖北",
#     "职业": "医生"
# }

# # 遍历键和值
# for key, value in person.items():
#     print(key, value)

# # 只遍历键
# for key in person.keys():
#     print(key)


# # 3. fromkeys() 创建字典
# print("\n=== 3. fromkeys() 创建字典 ===")
# keys = ["name", "age", "hobby"]

# # 默认值为 None
# d1 = dict.fromkeys(keys)
# print(d1)

# # 指定默认值
# d2 = dict.fromkeys(keys, "test")
# print(d2)


# # 4. 字典复制与浅拷贝
# print("\n=== 4. 字典复制与浅拷贝 ===")
# a = [12, "sing"]
# b = {20: "dance"}

# dict1 = {"Alex": a, "Thea": b}

# dict2 = dict1          # 直接赋值
# dict3 = dict1.copy()   # 浅拷贝

# dict1["Alex"] = b

# print("原字典：", dict1)
# print("直接赋值：", dict2)
# print("浅拷贝：", dict3)


# # 5. 嵌套字典
# print("\n=== 5. 嵌套字典 ===")
# data = {
#     "北京": {
#         "昌平": {
#             "沙河": ["oldboy", "test"],
#             "天通苑": ["链家地产"]
#         },
#         "朝阳": {
#             "望京": ["奔驰", "陌陌"],
#             "国贸": ["CICC"]
#         }
#     },
#     "山东": {
#         "青岛": {},
#         "济南": {}
#     }
# }

# # 访问嵌套字典
# print(data.keys())
# print(data["北京"].keys())
# print(data["北京"]["昌平"].keys())
# print(data["北京"]["昌平"]["沙河"])

# # 简单分层输出
# for province in data:
#     print(province)
#     for city in data[province]:
#         print("  ", city)


# # 6. 集合元素添加
# print("\n=== 6. 集合元素添加 ===")
# phones = {"华为", "苹果"}

# print(phones)

# phones.add("小米")                 # 添加一个元素
# phones.update(["Oppo", "Vivo"])    # 添加多个元素

# print(phones)


# # 7. 集合元素删除
# print("\n=== 7. 集合元素删除 ===")
# games = {
#     "世界杯排球赛",
#     "世界乒乓球锦标赛",
#     "世界篮球锦标赛",
#     "世界足球锦标赛"
# }

# print(games)

# games.remove("世界足球锦标赛")     # 删除指定元素
# games.discard("世界杯排球赛")      # 删除指定元素，不存在也不报错
# games.pop()                       # 随机删除一个元素

# print(games)

# games.clear()                     # 清空集合
# print(games)


# # 8. 集合并、交、差
# print("\n=== 8. 集合并、交、差 ===")
# a = {8, 9, 10, 11, 12, 13}
# b = {0, 1, 2, 3, 7, 8}

# print("并集：", a | b)
# print("交集：", a & b)
# print("差集：", a - b)

# # 也可以用函数写法
# print(a.union(b))
# print(a.intersection(b))
# print(a.difference(b))


# # 9. 迭代器对象
# print("\n=== 9. 迭代器对象 ===")
# nums = [1, 2, 3, 4]

# it = iter(nums)   # 创建迭代器

# while True:
#     try:
#         print(next(it))
#     except StopIteration:
#         break

print("""
|--- 欢迎进入通讯录程序 ---|
|--- 1. 查询联系人资料 ---|
|--- 2. 添加新的联系人 ---|
|--- 3. 删除已有联系人 ---|
|--- 4. 退出通讯录程序 ---|
""")

address_book = {}  # 保存联系人信息

while True:
    temp = input("请输入指令代码：")

    # 判断输入是否为数字
    if not temp.isdigit():
        print("输入错误，请输入 1-4 的数字。")
        continue

    item = int(temp)

    # 退出程序
    if item == 4:
        print("|--- 感谢使用通讯录程序 ---|")
        break

    # 查询联系人
    elif item == 1:
        name = input("请输入联系人姓名：")

        if name in address_book:
            print(name, ":", address_book[name])
        else:
            print("该联系人不存在！")

    # 添加或修改联系人
    elif item == 2:
        name = input("请输入联系人姓名：")

        if name in address_book:
            print("联系人已存在：", name, ":", address_book[name])
            choice = input("是否修改联系人电话？(Y/N)：")

            if choice == "Y" or choice == "y":
                phone = input("请输入新的联系人电话：")
                address_book[name] = phone
                print("联系人修改成功！")
            else:
                print("未修改联系人。")

        else:
            phone = input("请输入联系人电话：")
            address_book[name] = phone
            print("联系人添加成功！")

    # 删除联系人
    elif item == 3:
        name = input("请输入联系人姓名：")

        if name in address_book:
            del address_book[name]
            print("删除成功！")
        else:
            print("联系人不存在！")

    # 处理 1-4 之外的数字
    else:
        print("指令不存在，请输入 1-4。")

