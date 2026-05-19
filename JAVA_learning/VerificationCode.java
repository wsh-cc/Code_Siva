import java.util.Scanner;

public class VerificationCode {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        while (true) {
            System.out.println("请输入验证码的长度：(输入-1退出)");

            int length = sc.nextInt();
            if (length == -1) {
                break;
            }
            System.out.println("生成的验证码是：");
            System.out.println(getVerificationCode(length));
        }
        sc.close();
    }

    public static String getVerificationCode(int length) {
        String str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_";
        String ans = "";
        for (int i = 0; i < length; i++) {
            int index = (int) (Math.random() * str.length());
            ans += str.charAt(index);
                }        return ans;
    }
}