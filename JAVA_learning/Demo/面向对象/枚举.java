package Demo.面向对象;

public class 枚举 {
    public enum Season {
        SPRING("春天"),
        SUMMER("夏天"),
        AUTUMN("秋天"),
        WINTER("冬天");

        private String name;

        private Season(String name) {
            this.name = name;
        }
        public void getSeason(){
            System.out.println(name);
        }
    }
    public static void main(String[] args) {
        Season season = Season.SUMMER;
        // season.getSeason();
        System.out.println(season);
        Season arr[] = Season.values();
        for (int i = 0; i < arr.length; i++) {
            System.out.println(arr[i]);
        }
    }
    
}
