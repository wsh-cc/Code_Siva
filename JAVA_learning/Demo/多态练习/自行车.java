package Demo.多态练习;

public class 自行车 extends moveMachine{
    public 自行车() {
    }
    public 自行车(String sign, double speed) {
        super(sign, speed);
    }
    @Override
    public void move() {
        System.out.println("自行车移动");
    }

    public void ringbell() {
        System.out.println("自行车响铃");
    }
}
