package Demo.普通练习;

public class 两数之和 {
    public static void main(String[] args){
        int[] arr= {1,2,3,4,5,6,6};
        int target = 10;
        for (int i = 0; i < arr.length; i++) {
            for (int j = i + 1; j < arr.length; j++) {
                if (arr[i] + arr[j] == target) {
                    System.out.println("The two numbers are: " + arr[i] + " and " + arr[j]);
                }
            }
        }
    }
}
