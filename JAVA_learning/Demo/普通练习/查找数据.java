package Demo.普通练习;

import java.util.Scanner;

public class 查找数据 {
    public static void main(String[] args){
        Scanner sc = new Scanner(System.in);
        int[] arr ={1,2,3,4,5,6,7};
        int target = sc.nextInt();
        sc.close();
        for (int i =0;i<arr.length;i++){
            if (target==arr[i]){
                System.err.println("nice bro");
                return;
            }
        }
        System.out.print("not find");
        
    }
}
