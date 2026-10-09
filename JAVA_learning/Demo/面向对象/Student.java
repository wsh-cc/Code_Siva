package Demo.面向对象;

class Student {

    private String name;
    private int age;


    public Student() {
    }

    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
    public void study(){
        System.out.println(name+"正在学习");
    }
    public void sleep(){
        System.out.println(name+"正在睡觉");
    }
    public void eat(){
        System.out.println(name+"正在吃饭");
    }
}