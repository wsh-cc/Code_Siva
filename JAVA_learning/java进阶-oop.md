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
    private String name;
    private Integer age;
    private boolean gender;
    private String email;
    private String password;
    private Integer math;
    private Integer chinese;
    public void printAllScore(){//输出总成绩
        System.out.println("总成绩为："+(math+chinese));
    }
}
```
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
//   User user = new User("Rasion",20,true,"rasion@gmail.com","123456",100,100);
    return user;
}
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
        user.setName("Rasion");//传入数据给无参构造器对象
        user.setAge(20);
        user.setGender(true);
        user.setEmail("rasion@gmail.com");
        user.setPassword("123456");
        user.setMath(100);
        user.setChinese(100);
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
    private StaticAbout() {
    }
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

#### （三）、综合实战

需求：展示系统中的全部电影信息(每部电影展示：名称、价格)，允许用户根据电影编号查询出某个电影的详细信息。

详细见A2.com.rasion.oop.demo的三个文件

### 三、参考

1. 学习主要链接来源于[[黑马程序员](https://www.bilibili.com/video/BV1gb42177hm?p=49&vd_source=2140b8696bb75ad7bd33e1195bf24372)]
2.  其他可能用得上的链接