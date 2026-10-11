from user_service import (
    add_user,
    get_users,
    get_user_by_id,
    update_user,
    delete_user
)


def main():
    while True:
        print("\n1. 添加用户")
        print("2. 查看所有用户")
        print("3. 查询用户")
        print("4. 修改用户")
        print("5. 删除用户")
        print("0. 退出")

        choice = input("请选择: ")

        try:
            if choice == "1":
                name = input("姓名: ")
                age = input("年龄: ")
                email = input("邮箱: ")

                user = add_user(name, age, email)
                print("添加成功:", user)

            elif choice == "2":
                users = get_users()
                for u in users:
                    print(u)

            elif choice == "3":
                user_id = int(input("ID: "))
                user = get_user_by_id(user_id)
                print(user)

            elif choice == "4":
                user_id = int(input("ID: "))
                name = input("姓名: ")
                age = int(input("年龄: "))
                email = input("邮箱: ")

                user = update_user(user_id, name, age, email)
                print("修改成功:", user)

            elif choice == "5":
                user_id = int(input("ID: "))
                delete_user(user_id)
                print("删除成功")

            elif choice == "0":
                break
            
            
            
            else:
                print("输入错误")

        except ValueError as e:
            print("错误:", e)

        except Exception as e:
            print("系统异常:", e)


if __name__ == "__main__":
    main()