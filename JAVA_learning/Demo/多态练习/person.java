package Demo.多态练习;

public class person {
    private String name;
    private int age;
    private String sex;
    public person(){

    }   
    public person(String name, int age, String sex) {
        this.name = name;
        this.age = age;
        this.sex = sex;
    }

    public void setAge(int age) {
        this.age = age;
    }
    public int getAge() {
        return age;
    }
    public void setName(String name) {
        this.name = name;
    }
    public String getName() {
        return name;
    }
    public void setSex(String sex) {
        this.sex = sex;
    }
    public String getSex() {
        return sex;
    }
    public void useMachine(moveMachine machine) {
        machine.move();
        machine.ring();
     
        if(machine instanceof 汽车){
            汽车 car = (汽车) machine;
            car.honk();
        }else if(machine instanceof 自行车){
            自行车 bike = (自行车) machine;
            bike.ringbell();
        };
           System.out.println("-------------------");
    }
}
