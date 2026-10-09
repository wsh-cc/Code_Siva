package Demo.普通练习;

import java.util.Scanner;

public class 红包问题 {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        System.out.print("请输入红包总金额（元）：");
        double totalAmount = sc.nextDouble();
        System.out.print("请输入红包个数：");
        int numPackets = sc.nextInt();
        sc.close();
        for (int i = 1; i <= numPackets; i++) {
            if (i == numPackets) {
                System.out.printf("第%d个红包金额为：%.2f元\n", i, totalAmount);
                break;
            }
            double Randompacket = 0.01 + Math.random() * (totalAmount - 0.01);
            totalAmount -= Randompacket;
            System.out.printf("第%d个红包金额为：%.2f元\n", i, Randompacket);
        }
    }
}
