# 通讯录列表
cards = []


def show_menu():
    """
    显示菜单
    """
    print("=" * 30)
    print("欢迎使用通讯录管理系统")
    print("1. 添加联系人")
    print("2. 删除联系人")
    print("3. 查找联系人")
    print("4. 修改联系人")
    print("5. 显示所有联系人")
    print("0. 退出系统")
    print("=" * 30)


def add_card():
    """
    添加联系人
    """
    name = input("请输入姓名：")
    phone = input("请输入电话：")
    email = input("请输入邮箱：")

    card = {
        "name": name,
        "phone": phone,
        "email": email
    }

    cards.append(card)
    print("联系人添加成功！")


def delete_card():
    """
    删除联系人
    """
    name = input("请输入要删除的联系人姓名：")

    for card in cards:
        if card["name"] == name:
            cards.remove(card)
            print("联系人删除成功！")
            return

    print("未找到该联系人！")


def find_card():
    """
    查找联系人
    """
    name = input("请输入要查找的联系人姓名：")

    for card in cards:
        if card["name"] == name:
            print("找到联系人：")
            print("姓名：", card["name"])
            print("电话：", card["phone"])
            print("邮箱：", card["email"])
            return

    print("未找到该联系人！")


def update_card():
    """
    修改联系人
    """
    name = input("请输入要修改的联系人姓名：")

    for card in cards:
        if card["name"] == name:
            print("找到联系人，请输入新的信息：")

            new_name = input("请输入新的姓名：")
            new_phone = input("请输入新的电话：")
            new_email = input("请输入新的邮箱：")

            card["name"] = new_name
            card["phone"] = new_phone
            card["email"] = new_email

            print("联系人修改成功！")
            return

    print("未找到该联系人！")


def show_all_cards():
    """
    显示所有联系人
    """
    if len(cards) == 0:
        print("通讯录为空！")
        return

    print("所有联系人如下：")
    for card in cards:
        print("-" * 20)
        print("姓名：", card["name"])
        print("电话：", card["phone"])
        print("邮箱：", card["email"])


def main():
    """
    主函数
    """
    while True:
        show_menu()

        choice = input("请输入操作编号：")

        if choice == "1":
            add_card()
        elif choice == "2":
            delete_card()
        elif choice == "3":
            find_card()
        elif choice == "4":
            update_card()
        elif choice == "5":
            show_all_cards()
        elif choice == "0":
            print("退出通讯录系统！")
            break
        else:
            print("输入错误，请重新输入！")


# 程序入口
if __name__ == "__main__":
    main()