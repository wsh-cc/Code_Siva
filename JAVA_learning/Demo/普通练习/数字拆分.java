package Demo.普通练习;

public class 数字拆分 {
    public static void main (String[] args) {
        int num = 12345;

        while(num>0){
            System.out.print(num%10 +" ");
            num/=10;
        }
    }
}
