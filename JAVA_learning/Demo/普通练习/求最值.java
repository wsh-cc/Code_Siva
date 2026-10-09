package Demo.普通练习;

public class 求最值 {
    public static void main(String[] args){
        int[] arr= {1,2,3,4,5,6,6};
    int max = arr[0];
    
    for (int i = 1; i<arr.length;i++){
        if(arr[i]>max){
            max = arr[i];
        }
    }
    System.out.print("max value is : "+ max);
    }
}
