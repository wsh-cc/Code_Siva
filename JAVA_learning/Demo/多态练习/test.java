package Demo.多态练习;

public class test {
    public static void main(String[] args) {
        person p1 = new person("张三", 20,"男" );
        person p2 = new person("李四", 18, "女");
        moveMachine m1 = new 汽车("宝马", 200);
        moveMachine c1 = new 自行车("凤凰", 30);
        m1.move();
        m1.ring();
        c1.move();
        c1.ring();
        System.out.println("-------------------");
        p1.useMachine(m1);
        p2.useMachine(c1);
   
    }
}
