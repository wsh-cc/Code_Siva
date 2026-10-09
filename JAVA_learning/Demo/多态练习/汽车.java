package Demo.多态练习;

public class 汽车 extends moveMachine{
    public 汽车() {
    }
    public 汽车(String sign, double speed) {
        super(sign, speed);
    }
    @Override
    public void move() {
        System.out.println("汽车移动");
    }
    
    public void honk() {
        System.out.println("汽车响铃");
    }
    
}
