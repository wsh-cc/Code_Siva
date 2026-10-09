# JavaLearnA2-oop

### 一、介绍

A2简介：关于java面向对象以及基本语法的学习，加上一个综合实践。

### 二、基本语法

#### （一）、面向对象编程

**面向对象三大特征：封装、继承、多态。**

##### 1、**对象**

特殊的数据结构，一个实体，有属性和行为。也可以理解为一张表。

##### 2、**类（对象类）**

特殊的数据结构，有属性和行为。类只在计算机中加载一次。

```java
public class User {//定义一个对象类，并且定义了对象的属性和行为
    //user类
    private String name;
    private Integer age;
    private boolean gender;
    private String email;
    private String password;
    private Integer math;
    private Integer chinese;
    public User(String name, Integer age, boolean gender,String email, String password,Integer math, Integer chinese)//一个初始化的方法
    {
        this.name = name;
        this.age = age;
        this.gender = gender;
        this.email = email;
        this.password = password;
        this.math = math;
        this.chinese = chinese;
    }
    public void printAllScore(){//输出总成绩
        System.out.println("总成绩为："+(math+chinese));
    }
    public void CheckVirus(){
        for (int i=1; i<=7;i++){
            System.out.println("%d/7",i);
    }
    System.out.println("病毒查杀完成"); 
        
    }
}

```
描述事物的类叫JavaBean类，可以写属性和行为，带有main方法的类叫做测试类

##### 3、封装对象与方法

也把对象和对对象的处理封装到同一个类中，方便调用，节省代码量。
```java
public static void main(String[] args) {
    User s1=insert();
    print(s1);
}
//定义一个返回值为User对象的存储对象数据的方法
public static User insert(){
    User user = new User();//无参构造器返回对象
    user.setName("Rasion");
    user.setAge(20);
    user.setGender(true);
    user.setEmail("rasion@gmail.com");
    user.setPassword("123456");
    user.setMath(100);
    user.setChinese(100);
    return user;
}
//使用时User user = insert();  //调用insert方法，返回一个User对象

public static void print(User user){//定义一个打印对象的方法
    System.out.println("Name: "+user.getName());
    System.out.println("Age: "+user.getAge());
    System.out.println("Gender: "+user.isGender());
    System.out.println("Email: "+user.getEmail());
    System.out.println("Password: "+user.getPassword());
    user.printAllScore();//调用对象类中的方法
}
```
##### 4、内存分配

java在内存的JVM虚拟机上运行，JAVM虚拟机又分为**堆内存、栈内存和方法区**一同执行程序。堆是存放对象的地方，栈是存放方法的地方，方法区是放类文件的地方。

    变量存在栈里，变量指向对象，对象存在堆里，对象指向类，类存在方法区，将方法区中的方法调到栈中执行
    万物皆对象，一个数据由一个对应的对象处理，我们设计对象时就是在设计类（对象的模板）。

#### （二）、类的基本语法

##### 1、构造器

（1）、构造器：类中定义的方法，用来初始化对象，在类中定义的方法，称为方法，在类中定义的变量，称为属性。
名字与类名一致，无返回值，无参数，无返回值类型，无访问修饰符。

（2）、特点：**创建对象时，对象会自动调用构造器**，如果没有定义构造器，JVM会自动生成一个无参构造器。

（3）、应用场景：创建对象时，调用构造器，立即初始化对象成员变量的值。

（4）、注意：**类默认有一个无参构造器**(没有显示而已)，若你自己定义了有参构造器，那么JVM就不会自动生成一个无参构造器。
```java
public class User {
    //构造器，特殊方法，不能写返回值，名称与类名一致。
    public User() {System.out.println("==无参构造器执行了==");
    }//无参构造器
    public User(String name, Integer age, boolean gender, String email, String password, Integer math, Integer chinese) {
        this.name = name;
        this.age = age;
        this.gender = gender;
        this.email = email;
        this.password = password;
        this.math = math;
        this.chinese = chinese;
    }//有参构造器，构造器重载
}
//在mian方法中调用构造器
public class main() {
    public static void main(String[] args) {
        User user = new User();//无参构造器返回对象
        
        User s2 = new User("Rasion", 20, true, "rasion@gmail.com", "123456", 100, 100);
        //有参构造器返回对象,创建对象时，调用构造器，立即初始化对象。
    }
}
```
##### 2、this关键字

（1）、this 关键字：是一个变量，可以用在方法中，调用当前的方法的对象地址。

（2）、应用场景：解决变量名称冲突问题。（见有参构造器）。
```java
public void print(String name){//（二）、2、this关键字解决变量冲突问题
    System.out.println(name+this.name);//this.name拿到的是对象变量(成员变量)name,而不是局部变量name
}
```
##### 3、封装

（1）、封装的设计要求：**合理隐藏、合理暴露**。

（2）、（合理隐藏）**使用private关键字**封装变量，防止用户在其他类中随意对本类内的变量修改数据，只允许在本类中直接被访问。

（3）、（合理暴露）**使用getter和setter方法**，封装变量，让用户在类外直接调用，修改数据。
```java
    public void setAge(Integer age) {
        if(age>0&&age<150){
            this.age = age;
        }else{System.out.println("年龄不合法");}
        //此处为校验，但一般不在成员调用方法中进行，要在其他调用了setAge方法之后再校验。
        //这里最好只有this.age = age;
    }
```

##### 4、实体类(JavaBean)

（1）、实体类：只能用来封装数据的类，也叫JavaBean。

（2）、特点：**类中成员变量私有，提供getter和setter方法；类中需要一个无参构造器，和有参构造器可选**

（3）、应用场景：实体类的对象只负责数据的封装，不涉及任何业务逻辑。而数据的业务处理交给其他类的对象来完成，以实现数据和业务处理相分离（解耦）。

##### 5、static修饰成员变量

（1）、static关键字：修饰成员变量、方法、类，修饰后，该成员变量、方法、类属于类，而不是对象。

（2）、静态变量（类变量）：有static修饰，属于类，被类的全部对象共享，所有对象都可以访问。

（3）、实例变量（对象的变量）：没有static修饰，属于每个对象，每个对象都有自己的变量，对象可以访问。

（4）、应用场景：如果某一个数据只需要一份，并且希望能够被共享、访问、修改，则该数据被定义成静态变量。 （如用户类，记录了创建了多少个用户对象）
```java
public class User {
    static String name;//静态变量（类变量）
    int age;//实力变量（对象的变量）
}
public class main(){
    public static void main(String[] args) {
        User s1= new User();//s1对象
        User s2= new User();//s2对象
        //其中，s1和s2各自都有各自的age变量，但s1不能访问s2的age。
        //但name是静态变量，所有对象都可以访问，存储在类中的。
        //所以我们访问静态变量一般都直接用  类名.静态变量 如 User.name
        User.name="Rasion";
        s1.age=10;
        s1.name="Rasion1";
        s2.age=20;
        s2.name="Rasion2";
        System.out.println(User.name+s1.age+s1.name+s2.age+s2.name);
        //Rasion210Rasion220Rasion2
    }
}
```

##### 6、static修饰方法

（1）、static修饰静态方法：有static修饰的成员方法，属于类，最好用类名调用，少用对象名调用。

（2）、实例方法：无static修饰的成员方法，属于对象，用对象名调用，不能用类名调用。

    规范：如果一个方法只是为了做一个功能且不需要直接访问对象的数据，这个方法直接定义为静态方法。
    如果这个方法是关于对象的行为，需要访问对象的数据，这个方法必须定义为实例方法

（3）、比如在main方法中，我们直接调用其他方法，是用类名调用，只不过类名在同一类中可以忽略不写。（main方法是静态方法）

##### 7、工具类与静态方法

（1）、工具类：封装了多个静态方法，每个方法用来完成一个功能，给开发人员直接使用。

（2）、区别：实例方法需要创建最想来调用，此时对象占用内存，而静态方法不需要，可以减少内存消耗；静态方法可以用类名调用，调用方便，能节省内存。
```java
public class StaticAbout {//工具类
    //工具类没有创建对象的需求，建议讲工具类的构造器私有。
    private StaticAbout() {}
    public static String getCode(int n) {//静态方法与工具类
        String code = "";
        for (int i = 0; i < n; i++) {
            int type = (int) (Math.random() * 3);//0-9 1-26 2-26
            switch (type) {
                case 0:
                    code += (int) (Math.random() * 10);
                    break;
                case 1:
                    code += (char) (Math.random() * 26 + 'a');//得到小写字母的区间
                    break;
                case 2:
                    code += (char) (Math.random() * 26 + 'A');
            }
        }
        return code;
    }
}
```
##### 8、静态方法与实例方法访问注意事项

（1）、静态方法中可直接访问静态成员，不可直接访问实例成员。

（2）、实例方法中即可直接访问静态成员，也可直接访问实例成员。

（3）、实例方法中可以出现this关键字，静态方法中不可出现this关键字。
```java
public class Attention{
    public static int count=100;//静态变量
    public static void print(){//静态方法
        System.out.println("Hello World!");
    }
    public String name;//实例变量，属于对象
    public void prints(){//实例方法，属于对象
    }
    public static void main(String[] args) {

    }
    //（1）、静态方法中可直接访问静态成员，不可直接访问实例成员。
    public static void printTest1(){
        System.out.println(count);
        print();
        //System.out.println(name);//报错
        //prints();//报错
        //System.out.println(this);//报错，this代表的只能是对象
        System.out.println(Attention.count);
    }
    //（2）、实例方法中即可直接访问静态成员，也可直接访问实例成员。
    public void printTest2(){
        System.out.println(count);
        print();
        System.out.println(name);
        prints();
        System.out.println(this);//实例方法中，this代表的是当前对象
    }
}
```
##### 9.final修饰类、方法、变量
```java
1.final修饰的变量不能被修改//可以是数值也可以是地址，但地址对应的对象的内容可以被修改。
2.常量名要大写，多个单词要用下划线隔开
```

#### (三)面向对象高级

##### 10.枚举类

```
public enum 枚举类名{
	枚举项1，枚举项2，枚举项3;
	属性;
	行为;
}
```

```java
public enum Season {
    SPRING("春天"),//等同于
    SUMMER("夏天"),
    AUTUMN("秋天"),
    WINTER("冬天");
//≈ public static final Season SPRING = new Season("春天");
    
    private String name;//season 有name这个属性
    private Season(String name) {   // 构造方法，默认也是private，这样外界也就不能构造（new）了
        this.name = name;
    }//可以空构造，前面就是 spring() 了

    public String getName() {
        return name;
    }
}

public static void main(String[] args) {//test
        Season season = Season.SUMMER;
        // season.getSeason();输出夏天
        System.out.println(season);//输出SUMMER,这是直接把对象
    }
```

理解：

```java
SPRING("春天")
≈ public static final Season SPRING = new Season("春天");

"春天"
   ↓
Season(String name)
   ↓
this.name = name
   ↓
SPRING对象中的 name = "春天"
```

**记住：**

- 枚举 = 对象数量固定的特殊类
- 枚举常量 ≈ `public static final` 对象
- 有参数 `SPRING("春天")` → 必须有对应构造方法
- 没参数 `SPRING` → 可以不写构造方法
- 枚举对象不能自己 `new`，直接用 `Season.SPRING`

```
values 和valueOf

values()
枚举类 → 所有枚举对象

valueOf("名字")
字符串 → 对应的枚举对象
```

##### **11.继承extends**

###### 一、继承的基本特点

- 使用 `extends` 实现继承。
- 单继承：一个子类只能直接继承一个父类。
- 多层继承：A → B → C。
- 所有类直接或间接继承 `Object`。
- 作用：代码复用、方法重写、实现多态。

```java
class Animal {
    public void eat() {
        System.out.println("吃东西");
    }
}

class Dog extends Animal {}

Dog dog = new Dog();
dog.eat(); // 吃东西
```

###### 二、继承中的成员特点

\1. 成员变量：**同名隐藏**

```java
class Father {
    int age = 40;
}

class Son extends Father {
    int age = 20;

    void show() {
        System.out.println(this.age);  // 20
        System.out.println(super.age); // 40
    }
}
```

- `this.age`：从当前类开始查找成员变量。
- `super.age`：从父类开始查找成员变量。
- 成员变量不能重写，只能隐藏。

\2. 成员方法：可以重写

```java
class Father {
    public void show() {
        System.out.println("父类");
    }
}

class Son extends Father {
    @Override
    public void show() {
        System.out.println("子类");
    }

    void test() {
        this.show();  // 子类
        super.show(); // 父类
    }
}
```

- **`@Override`：**标识方法重写。
- **`private`、`final` 方法不能重写。**
- `static` 方法只能隐藏，不能重写。

\3. 构造方法：不能继承

```java
class Father {
    public Father() {
        System.out.println("父类构造");
    }
}

class Son extends Father {
    public Son() {
        super(); // 可省略
        System.out.println("子类构造");
    }
}
```

执行 `new Son()`：

```
父类构造
子类构造
```

- 创建子类对象时，先执行父类构造，再执行子类构造。
- 子类构造方法**默认**调用 `super()`。
- 父类没有可访问的无参构造时，需要指定合适的父类构造调用。

###### 三、this 与 super

| 作用     | this          | super          |
| -------- | ------------- | -------------- |
| 成员变量 | `this.name`   | `super.name`   |
| 成员方法 | `this.show()` | `super.show()` |
| 无参构造 | `this()`      | `super()`      |
| 有参构造 | `this(参数)`  | `super(参数)`  |

\1. this()：调用本类构造方法

```java
class Student {
    public Student() {
        this("张三");
        System.out.println("无参构造");
    }

    public Student(String name) {
        System.out.println(name);
    }
}
```

执行 `new Student()`：

```
张三
无参构造
```

\2. super()：调用父类构造方法

```java
class Father {
    public Father(int age) {
        System.out.println(age);
    }
}

class Son extends Father {
    public Son() {
        super(40);
        System.out.println("子类构造");
    }
}
```

执行 `new Son()`：

```
40
子类构造
```

###### 四、注意事项

1. `this` 表示当前对象，`super` 用于访问父类成员或调用父类构造。
2.    `this()` 调用本类构造，`super()` 调用父类构造。
3. 一个构造方法不能同时显式调用 `this()` 和 `super()`。
4. 构造方法不能循环调用。
5. 传统写法中，`this()`、`super()` 必须位于构造方法第一条语句（Java 25 起有条件放宽）。
6. 静态方法中不能使用 `this` 或 `super` 访问实例成员。

###### 五、核心总结

- 成员变量： 同名隐藏。
- 成员方法： 可以重写。
- 构造方法： 不能继承，先父后子。
- this： 当前对象、本类构造。
- super： 父类成员、父类构造。

##### 12.四种权限修饰符

| 修饰符       | 本类 | 同包 | 不同包子类 | 不同包其他类 |
| ------------ | ---- | ---- | ---------- | ------------ |
| `public`     | ✅    | ✅    | ✅          | ✅            |
| `protected`  | ✅    | ✅    | ✅          | ❌            |
| 默认（不写） | ✅    | ✅    | ❌          | ❌            |
| `private`    | ✅    | ❌    | ❌          | ❌            |

##### **13.多态**

###### 一、多态的条件

继承关系、方法重写、父类引用指向子类对象。

```java
class Father {
    int age = 40;

    public void show() {
        System.out.println("父类");
    }
}

class Son extends Father {
    int age = 20;

    @Override
    public void show() {
        System.out.println("子类");
    }

    public void play() {
        System.out.println("玩游戏");
    }
}
```

###### 二、多态的成员访问特点

```java
Father f = new Son();

System.out.println(f.age); // 40，变量看左边
f.show();                  // 子类，重写方法看右边
// f.play();               // 报错，父类没有该方法
```

- 成员变量：看引用类型。
- 普通实例方法：编译看左边，运行看右边（发生重写时）。
- static 方法：看引用类型，不参与重写。
- 子类独有方法：父类引用不能直接调用。

###### 三、向上转型与向下转型

```java
Father f = new Son(); // 向上转型，自动

Son s = (Son) f;     // 向下转型，显式
s.play();            // 调用子类独有方法
```

安全转换：

```java
if (f instanceof Son) {//向下转型，进行判断防止报错
    Son s = (Son) f;
    s.play();
}
```

###### 四、多态的作用

```java
public static void test(Father f) {
    f.show();
}

test(new Father()); // 父类
test(new Son());    // 子类
```

一个方法可以接收不同子类对象，执行不同实现，提高扩展性。

核心记忆：

- 多态：`Father f = new Son();`//编译看左边，运行看右边

  | 成员类型       | 判断规则               |
  | -------------- | ---------------------- |
  | 成员变量       | 编译、访问都看左边     |
  | `static` 方法  | 看左边                 |
  | 重写的实例方法 | 编译看左边，运行看右边 |

- 向**上转型自动**，向下转型显式。

- **变量和静态方法看左边。**

- **重写的实例方法看右边。**

- 子类独有方法需要向下转型才能通过父类引用调用。



​    
