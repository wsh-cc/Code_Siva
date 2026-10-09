package Demo.多态练习;

public class moveMachine {
    private String sign;
    private double speed;
    public moveMachine() {
    }
    public moveMachine(String sign, double speed) {
        this.sign = sign;
        this.speed = speed;
    }
    public void move() {
        System.out.println("移动机器");
    }
    public void ring() {
        System.out.println("移动机器响铃");
    }
    public String getSign() {
        return sign;
    }
    public void setSign(String sign) {
        this.sign = sign;
    }
    public double getSpeed() {
        return speed;
    }
    public void setSpeed(double speed) {
        this.speed = speed;
    }
}
