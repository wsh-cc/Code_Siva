import java.util.Random;
import java.util.Scanner;

public class guassnumber {
    public static void main(String[] args) {

        guass();
    }

    public static void guass() {
        int number = gernerate(100, 999);
        System.out.println("请输入你猜的数字：");
        Scanner sc = new Scanner(System.in);
        while (true) {

            int guas = sc.nextInt();
            if (check(number, guas)) {
                break;
            } else {
                System.out.println("请继续猜");
            }
        }
        sc.close();
    }

    public static int gernerate(int Min, int Max) {
        return new Random().nextInt(Max - Min + 1) + Min;

    }

    public static boolean check(int number, int guas) {
        if (number > guas) {
            System.out.println("猜小了");
        } else if (number < guas) {
            System.out.println("猜大了");
        } else {
            System.out.println("猜对了");
            return true;
        }
        return false;
    }
}
