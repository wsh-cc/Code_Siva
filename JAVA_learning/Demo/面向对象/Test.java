package Demo.面向对象;


import java.util.Random;

public class Test {
    public static void main(String[] args) {
        // 创建一个Person对象
        Random r = new Random();
        double num1 = r.nextDouble(1,1.000001);
        System.out.println(num1);
    }
}
