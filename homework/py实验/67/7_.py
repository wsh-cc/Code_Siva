

class Book:
    def __init__(self, name, price, status=False):
        self.name = name
        self.price = price
        self.status = status

    def __str__(self):
        state = "已借出" if self.status else "未借出"
        return f"书名：{self.name}，价格：{self.price}，状态：{state}"


class BookManager:
    def __init__(self):
        self.books = [
            Book("Python程序设计", 49.9),
            Book("数据库基础", 39.8),
            Book("计算机网络", 45.0)
        ]

    def menu(self):
        while True:
            print("\n===== 图书管理系统 =====")
            print("1. 查询所有书籍")
            print("2. 添加书籍")
            print("3. 借出书籍")
            print("4. 退出系统")

            choice = input("请输入功能编号：")

            if choice == "1":
                self.show_all_books()
            elif choice == "2":
                self.add_books()
            elif choice == "3":
                self.lend_books()
            elif choice == "4":
                print("已退出图书管理系统")
                break
            else:
                print("输入错误，请重新输入")

    def show_all_books(self):
        if len(self.books) == 0:
            print("当前没有书籍")
            return

        print("\n当前书籍信息如下：")
        for book in self.books:
            print(book)

    def add_books(self):
        name = input("请输入书籍名称：")
        price = float(input("请输入书籍价格："))

        if self.check_books(name):
            print("该书籍已存在，不能重复添加")
        else:
            book = Book(name, price)
            self.books.append(book)
            print("书籍添加成功")

    def lend_books(self):
        name = input("请输入要借出的书籍名称：")
        book = self.check_books(name)

        if book is None:
            print("该书籍不存在")
        elif book.status:
            print("该书籍已经被借出")
        else:
            book.status = True
            print("借书成功")

    def check_books(self, name):
        for book in self.books:
            if book.name == name:
                return book
        return None


if __name__ == "__main__":
    manager = BookManager()
    manager.menu()

