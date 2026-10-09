package Demo.普通练习;

import java.util.Scanner;

public class 练习 {
    public static void main(String[] args) {
        Scanner sc  = new Scanner (System.in);
        int [] arr = new int[5];
        int sum = 0;
        for(int i=0;i<5;i++)
        {
            arr[i]=sc.nextInt();
            if(arr[i]<0 || arr[i]>100)
            {
               while(arr[i]<0 || arr[i]>100)
               {
                   System.out.println("please input again");
                   arr[i]=sc.nextInt();
               }
            }
            sum += arr[i];
        }
        sc.close();
        int max = tomax(arr);
        int min = tomin(arr);
        System.out.println("average scores is : "+(sum-max-min)/3);
       
    }
    public static int tomax(int[] args)
    {
        int max = args[0];
        for (int i = 1; i < args.length; i++) {
            if (args[i] > max) {
                max = args[i];
            }
        }
        return max;
    }
      public static int tomin(int[] args)
    {
        int min = args[0];
        for (int i = 1; i < args.length; i++) {
            if (args[i] < min) {
                min = args[i];
            }
        }
        return min;
    }
    
}
