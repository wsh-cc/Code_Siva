// import java.util.Scanner;

public class test {
    public static void main() {
        // printhello(5);
        // printtype();
        // System.out.println("hello world");
        // jinzhi();
        // typeconversion();
        // System.out.println(expression(10, (byte) 20, 30.5, 'A'));
        // System.out.println(expression((byte) 10, (byte) 20));

        // Scanner scanner = new Scanner (System.in);
        // int n = scanner.nextInt();
        // System.out.println("你输入了；"+ n);
        // scanner.close();

        // System.out.println( 10+'b'+"aaa");// 运算+连接
        // System.out.println("abc" + 10 + 'b');// 连接

        // String arr[] = { "hello", "world" };// char类型的数组
        // String name = "hello world";
        // String[] stus = new String[10];
        // String name1 = "";
        // String arr1[] = new String[] {};
        // System.out.println(arr[1]);// 字符串长度
        // System.out.println(name.charAt(0));// 获取字符串中指定位置的字符
        // System.out.println(name1);// 获取字符串长度

        // dynamicArry();
    }

    public static void printhello(Integer n) {
        for (int i = 0; i < n; i++) {
            System.out.println("hello world" + i);
        }
    }

    public static void printtype() {
        System.out.println("byte类型：" + Byte.MAX_VALUE + " " + Byte.MIN_VALUE);
        System.out.println("short类型：" + Short.MAX_VALUE + " " + Short.MIN_VALUE);
        System.out.println("int类型：" + Integer.MAX_VALUE + " " + Integer.MIN_VALUE);
        System.out.println("long类型：" + Long.MAX_VALUE + " " + Long.MIN_VALUE);
        System.out.println("float类型：" + Float.MAX_VALUE + " " + Float.MIN_VALUE);
        System.out.println("double类型：" + Double.MAX_VALUE + " " + Double.MIN_VALUE);
        System.out.println("char类型：" + Character.MAX_VALUE + " " + Character.MIN_VALUE);
        System.out.println("boolean类型：" + true + "_0_ " + false);
    }

    public static void jinzhi() {
        int l1 = 0b1010; // 二进制以0b开头
        int l2 = 012; // 八进制以0开头
        int l3 = 0x12; // 十六进制以0x开头
        System.out.println("二进制1010的十进制值：" + l1);
        System.out.println("八进制12的十进制值：" + l2);
        System.out.println("十六进制12的十进制值：" + l3);
    }

    public static void typeconversion() {
        double c = 10.911;// double为8位浮点数，int为4位整数
        int d = (int) c;// 强制类型转换,若数据过大，强转后数据溢出，则结果为出错
        System.out.println(d);// 强制转换后只会把double的后4位转换为int，丢掉小数保留整数
        System.out.println((int) c);
    }

    public static double expression(int a, byte b, double c, char d) {
        return a + b + c + d;
    }

    public static int expression(byte a, byte b) {
        return a + b;
    }

    public static void dynamicArry() {
        Integer[] scores = new Integer[10];
        for (int i = 0; i < scores.length; i++) {
            scores[i] = (int) (Math.random() * 100) + 1;// 生成1-100的随机整数 Math.random()// 生成0~1之间的随机小数
            /*
             * System.out.println("请输入第"+(i+1)+"个学生的成绩：");
             * scores[i] = new Scanner(System.in).nextInt(); // 从键盘输入成绩
             */

        }
        // for (int i = 0; i < scores.length; i++) {
        // System.out.println("第" + (i + 1) + "个学生的成绩为：" + scores[i]);
        // }
        int index = (int) (Math.random() * scores.length);
        System.out.println("index 为" + index + "成绩为 " + scores[index]);
    }

    public static void arrmax(Integer[] arr) {
        Integer max = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        System.out.println("最大值为：" + max);
    }

    public static void arraysort(Integer[] sc){
        for (int i =0; i<sc.length;i++){
            for (int j=0; j<sc.length-i-1;j++){
                if (sc[i]>sc[j+1]){
                    int temp = sc[j];
                    sc[j] =sc[j+1];
                    sc[j+1] = temp;
                }
            }
        }
    }

      
}
