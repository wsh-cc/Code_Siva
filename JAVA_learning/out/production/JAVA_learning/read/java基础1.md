# JavaLearnA1

### 一、介绍

A1简介：关于java的基本语法学习，加上一个综合实践

### 二、基本语法

#### （一）、功能单元

```java
    public static void printHello(int n){//（一）、创建输出功能
        for(int i=1;i<n+1;i++)
        System.out.println("Hello world"+i);
    }
```
#### （二）、注释

    单行注释：//
    
    多行注释：/* */
    
    文档注释：/**
            *这是文档注释
           * */

#### （三）、字面量

    即：掌握数据在程序中的书写格式

```java
    System.out.println("Hello world");//字符串
    System.out.println(true);//布尔值
    System.out.println(false);//布尔值
    System.out.println(1);//整数
    System.out.println(1.0);//浮点数
    System.out.println('a');//字符
    System.out.println("a");//字符串
            //特殊字符
    System.out.println("Hello\nworld");//换行
    System.out.println("Hello\tworld");//制表符
    System.out.println("Hello\"world");//双引号
    System.out.println("Hello\'world");//单引号
    System.out.println("Hello\rworld");//回车
    System.out.println("Hello\bworld");//退格
    System.out.println("Hello\fworld");//换页
    System.out.println("Hello\tworld");//制表符
    System.out.println("Hello\u0000world");//Unicode码
```

#### （四）、变量

    即：变量就是用来装数据的容器，变量有类型，变量有名称，变量有值。

格式：**数据类型 变量名 = 值;**

    注意：
    数据类型：int、double、char、boolean、String、long、float、short、byte
    变量可以改变值，但类型不能改变。
    ——————————————————————————————————————
    变量的数据存储原理（文本、图片、音频）：
    文本：ASCII码表（0-127）
    图片：RGB
    音频：（波形图）采样率、采样位深、采样位宽、采样精度、采样范围。

| 数据类型    | 数据范围byte                           |
| ----------- | -------------------------------------- |
| byte        | -126~127                               |
| short       | -32768~32767                           |
| int（默认） | -2147483648~2147483647（10位数，21亿） |
| long        | -2^63~ 2^63-1                          |
| float       | -3.4E+38 ~ 3.4E+38（4字节）            |
| double      | -1.7E-308 ~ 1.7E+308                   |
| char        | 0 - 65535                              |
| boolean     | true\false                             |

#### （五）、数据类型

```java
    System.out.println("byte类型："+Byte.MAX_VALUE+" "+Byte.MIN_VALUE);
    System.out.println("short类型："+Short.MAX_VALUE+" "+Short.MIN_VALUE);
    System.out.println("int类型："+Integer.MAX_VALUE+" "+Integer.MIN_VALUE);
    System.out.println("long类型："+Long.MAX_VALUE+" "+Long.MIN_VALUE);
    System.out.println("float类型："+Float.MAX_VALUE+" "+Float.MIN_VALUE);
    System.out.println("double类型："+Double.MAX_VALUE+" "+Double.MIN_VALUE);
    System.out.println("char类型："+Character.MAX_VALUE+" "+Character.MIN_VALUE);
    System.out.println("boolean类型："+true+" "+false);
```

#### （六）、标识符与关键字

关键字：关键字是编程语言中预定义的具有特殊意义的单词。这些单词被保留，不能用作标识符来命名变量。

标识符：标识符是程序中用来唯一标识变量、方法、类、接口、数组等名称的。标识符不能以数字开头，不能包含空格，不能包含特殊字符，不能包含中文。

#### （七）、方法

定义：方法是用来封装一段代码，让代码更加 modular、reusable、readable，方法代表一个功能，可以接收数据并进行处理，返回处理后的结果。

    方法完整格式：修饰符 返回值类型 方法名(参数列表){方法体（需要执行的功能代码）}

方法调用：**方法名（参数列表）**

    注意：
    方法的返回值：无返回值void类型和有返回值的数据类型。
    方法的参数：无参数、有参数。
    方法可以重载的：方法名相同，参数列表不同。通过方法名称标记同一功能，通过参数进行差异化。
    无返回值的方法可以直接通过单独的return语句，立即结束当前方法的执行。

#### （八）、类型转换

1、存在不同类型的变量赋值给其他类型的变量，称为类型转换。

2、自动类型转换：范围小的数据类型可以自动转换为范围大的数据类型，如：int转long、float转double。

3、强制类型转换：范围大的数据类型不能直接转换为范围小的数据类型，需要使用强制类型转换。

```java
    double c=10.0;//double为8位浮点数，int为4位整数
    int d=(int)c;//强制类型转换,若数据过大，强转后数据溢出，则结果为出错
    System.out.println(d);//强制转换后只会把double的后4位转换为int，丢掉小数保留整数
    System.out.println((int) c);
```

#### （九）、表达式的自动类型提升

1、表达式的最终结果类型是由表达式中的最高类型决定的。

2、在表达式中，如果存在byte、short、char类型，则表达式中的所有数据类型都会自动提升为int类型。

```java
    public static double expression(int a, byte b, double c, char d){
        return a+b+c+d;
    }
    public static int expression(byte a,byte b){
        return a+b;
    }
```

#### （十）、输入输出

1、输入：程序读取用户输入的数据。

```java
    Scanner scanner=new Scanner(System.in);//创建一个Scanner扫描对象
    int n=scanner.nextInt();//获取用户输入的整数
    double d=scanner.nextDouble();//获取用户输入的浮点数
    String s=scanner.nextLine();//获取用户输入的字符串
    
```
2、输出：程序向用户输出数据。（System.out.println）

#### （十一）、运算符

1、算术运算符：+、-、*、/、%

2、关系运算符：==、!=、>、<、>=、<=

3、逻辑运算符：&&、||、!

4、位运算符：&、|、^、~、<<、>>、>>>

5、赋值运算符：=、+=、-=、*=、/=、%=

6、其他运算符：&、|、^、~、<<、>>、>>>、?:
```java
    int a=10;
    int b=20;
//若自增自减单独使用，不用区分运算符是否在前或后，结果都一样
    int c=++a;//先自增再赋值，此时c=11,a=11
    System.out.println("先自增再赋值：c="+c+" a="+a);
    int d=a++;//先赋值再自增，此时d=11,a=12
    System.out.println("先赋值再自增：d="+d+" a="+a);
    
    System.out.println("加法：a+b="+(a+b));//加法
    System.out.println(a+'b'+"abc");//运算+连接
    System.out.println("abc"+a+'b');//连接
    System.out.println("减法：a-b="+(a-b));//减法
    System.out.println("乘法：a*b="+a*b);//乘法
    System.out.println("除法：a/b="+a/b);//除法
    System.out.println("取余：a%b="+a%b);//取余
```

#### （十二）、赋值

1、赋值运算符：=、+=、-=、*=、/=、%=（先运算后赋值，a=a+b）

3、三元表达式：表达式？值1：值2（真：假）

#### （十三）、数组（见Array.java）

1. 创建数组：类型[] 数组名 = new 类型[数组长度];


**静态初始化数组：类型[ ] 数组名 = {数组元素1,数组元素2...};**

    数组是一个容器，可以存储多个相同类型的数据。
    数组的访问：数组名[索引]。
    数组的长度：数组名.length。

```java
//以下三种方法都是可行的，都是静态初始化数组
    String[] names = {"吴十", "郑十一", "王十二"};
    String[] names = new String[]{"吴十","郑十一","王十二"};
    String names[] = new String[]{"吴十", "郑十一", "王十二"};
```
**2、动态初始化数组：类型[ ] 数组名 = new 类型[长度];**//只确定数组类型与长度，其中内容都是默认值

| 数据类型                     | 动态初始化数组元素默认值 |
| ---------------------------- | ------------------------ |
| byte、short、int、long、char | 0                        |
| float、double                | 0.0                      |
| boolean                      | false                    |
| 类、接口、数组、String       | null                     |

```java
    public static void dynamicArray() {//2、创建数组，动态初始化数组
        //定义一个数组，存储10个学生姓名
        Integer[] scores = new Integer[10];
        //录入10名学生成绩，存到数组中去
        for (int i = 0; i < scores.length; i++) {
//            System.out.println("请输入第" + (i + 1) + "个学生的成绩：");
//            scores[i] = new Scanner(System.in).nextInt();
            scores[i] = (int)(Math.random() * 100);
        }
        int index = (int) (Math.random() * scores.length);
        System.out.println("第"+(index+1)+"个人成绩是："+scores[index]);for
    }
```
3、求数组中的最大值
```java
    public static Integer arrayMax(Integer[] sc) {//3、获取数组中的最大值
        Integer max = sc[0];
        for (int i = 0; i < sc.length; i++) {
            if (sc[i] > max) {
                max = sc[i];}
        }
        return max;
    }
```

4、对数组进行排序
```java
    public static void arraySort(Integer[] sc) {//4、对数组进行排序
        for (int i = 0; i < sc.length; i++) {
            for (int j = 0; j < sc.length - i - 1; j++) {
                if (sc[j] > sc[j + 1]) {
                    int temp = sc[j];
                    sc[j] = sc[j + 1];
                    sc[j + 1] = temp;
                }
            }
        }
        for (int i = 0; i < sc.length; i++) {
            System.out.println(sc[i]);
        }
    }
```

**5、数组实践：扑克牌乱序发放（Poker）**

#### （十四）、二维数组

1、静态初始化二维数组：**类型[][] 数组名 = { {元素1,元素2...}, {元素1,元素2...}...};**

2、动态初始化二维数组：**类型[][] 数组名 = new 类型[行数][列数];**

3、把二维数组的某一行存为一个一维数组：**类型[ ] 一维数组名 = 二维数组名[第n行];**

4、 访问长度：**数组名.length**
```java
System.out.println(二维数组名.length);//访问有几个一维数组
System.out.println(二维数组名[0].length);//访问第0行的长度
```

**5、二维数组的实践：打乱二维数字（NumberPuzzle）**

#### （十五）、综合实践

##### 1、猜数字(GuessNumber)
说明：猜数字游戏，计算机随机生成一个三位数，用户输入一个数字，计算机判断数字大小，如果猜对了，游戏结束，否则继续猜。(见A1的GuessNumber类或如下代码)
```java
package com.rasion.main;
import java.util.Scanner;
import static com.rasion.main.BasicJava.getRandom;
public class GuessNumber {
    public static void main(String[] args) {
        while (true) {
            guessNumberInterface();
            if (scannerNumber() == 2) {
                System.out.println("游戏结束");
                break;
            } else {
                int a = getRandom(3);//这里给的是三位数
                int b = 0;
                while (true) {
                    System.out.println("请输入一个数字");
                    b = scannerNumber();
                    ifOrnot(b, a);
                    if (a == b) {
                        break;
                    }
                }
            }
        }
    }

    public static void guessNumberInterface() {
        System.out.println("======猜数字游戏======");
        System.out.println("      1.开始游戏");
        System.out.println("      2.退出游戏");
    }

    public static int scannerNumber() {
        Scanner sc = new Scanner(System.in);
        return sc.nextInt();
    }

    public static void ifOrnot(Integer a, Integer b) {
        if (a > b) {
            System.out.println("猜大了");
        } else if (a < b) {
            System.out.println("猜小了");
        } else {
            System.out.println("猜对了");
            return;
        }
//        System.out.println("数字是"+b);
    }
}
```

**注意：其中随机数也可以为：**
```java
    import java.util.Random;
    Random random=new Random();
    int number=random.nextInt(100);//生成0-99的随机数
    int n=random.nextInt(25)+25;//生成25-50间的随机数
```

##### 2、验证码(VerificationCode)
说明：可以生成一个指定位数的验证码，验证码由数字和字母组成。(见A1的VerificationCode类或如下代码)
```java
package com.rasion.main;
import java.util.Scanner;
public class VerificationCode {
    public static void main(String[] args) {
        //生成指定位数的验证码，验证码由数字、大小写字母组成
        System.out.println("请输入验证码位数：");
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();//验证码位数
        System.out.println(getCode(n));
    }
    public static String getCode(int n) {
        String code = "";
        for (int i = 0; i < n; i++) {
            int type = (int) (Math.random() * 3);//0-9 1-26 2-26
            switch (type) {
                case 0:
                code += (int) (Math.random() * 10);
                break;
                case 1:
                code += (char) (Math.random() * 26 + 'a');
                break;
                case 2:
                code += (char) (Math.random() * 26 + 'A');
            }
        }
        return code;
    }
}
```
##### 3、找到所有素数(FindPrime)

说明：在1-1000之间找到所有素数。(见A1的FindPrime类或如下代码)
```java
package com.rasion.main;
public class FindPrime {
    public static void main(String[] args) {
    //找到所有素数
    int temp=0;
    for(int i=1;i<=1000;i++){
        if(isPrime(i)){
                temp++;
                System.out.print(i+"\t ");
                if(temp%10==0) System.out.println();//十个为一排
            }
        }
    }
    public static boolean isPrime(int n) {//判断是否为素数
        if (n<=1){return false;}
        for(int i=2;i<=Math.sqrt(n);i++){
            if(n%i==0){return false;}
        }
        return true;
    }
}
```

##### 4、扑克牌乱序发放（Poker）

##### 5、打乱二维数字（NumberPuzzle）

### 三、参考

1. 学习主要链接来源于[[黑马程序员](https://www.bilibili.com/video/BV1gb42177hm?p=1&amp;vd_source=2140b8696bb75ad7bd33e1195bf24372)]: https://www.bilibili.com/video/BV1gb42177hm?p=1&amp;vd_source=2140b8696bb75ad7bd33e1195bf24372
2.  其他可能用得上的链接