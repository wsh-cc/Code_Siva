package Demo.多态练习;

public class son extends person {
    private String uid;

    public void setname(String uid) {
        this.uid = uid;
    }

    public void getname() {
        System.out.println(this.uid);
    }
    public String getUid() {
        return uid;
    }
    public son() {
    }

    public son(String uid) {
        this.uid = uid;
    }

    public son(String name, int age, String sex, String uid) {
        super(name, age, sex);
        this.uid = uid;
    }

}
