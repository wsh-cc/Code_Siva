package Demo.多态练习;

public class test1 {
    public static void main(String[] args) {
       son t1 = new son("张三", 20, "男", "123456");
       System.out.println(t1.getName());
       System.out.println(t1.getAge());
       System.out.println(t1.getUid());
    }
}
