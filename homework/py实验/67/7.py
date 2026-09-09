
class Student:
    def __init__(self, name, age):
        self.name = name          # 公有成员
        self.__age = age          # 私有成员

    def show_info(self):
        print("姓名：", self.name)
        print("年龄：", self.__age)


stu = Student("张三", 20)
print(stu.name)
stu.show_info()

class Person:
    def __init__(self):
        self.__name = "李四"

    def get_name(self):
        return self.__name


class StudentChild(Person):
    def show(self):
        # print(self.__name)  # 子类不能直接访问父类私有成员
        print("通过公有方法访问：", self.get_name())


stu = StudentChild()
stu.show()

class Car:
    brand = "比亚迪"   # 类成员

    def __init__(self, color):
        self.color = color   # 实例成员

    def show(self):
        print("品牌：", Car.brand)
        print("颜色：", self.color)


car1 = Car("黑色")
car2 = Car("白色")

car1.show()
car2.show()


class Animal:
    def speak(self):
        print("动物会叫")


class Dog(Animal):
    def speak(self):
        print("狗会汪汪叫")


class Cat(Animal):
    def speak(self):
        print("猫会喵喵叫")


dog = Dog()
cat = Cat()

dog.speak()
cat.speak()

