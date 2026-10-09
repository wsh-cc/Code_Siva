package Demo.普通练习;

public class 查找元素 {
    public static void main(String[] args){
        int[] arr= {1,2,3,4,6,6};
        int target = 5;
        int index = -1;
        boolean found = false;
        for (int i=0;i<arr.length;i++){
            if(arr[i]<=target&&!found){
                if (arr[i]==target){
                    System.out.println("Element found at index: " + i);
                    found = true;
                }
            }else{
                index = i;
                break;
            }
        }
        if (!found) {
            System.out.println("Element need place is: " + index);
        }
    }
}
