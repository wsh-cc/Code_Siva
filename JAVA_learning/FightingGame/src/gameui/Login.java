package FightingGame.src.gameui;

import FightingGame.src.Bean.user;
import FightingGame.src.util.generatecode;

import java.util.ArrayList;
import java.util.Scanner;


public class Login {
    public void start() {

        ArrayList<user> list = new ArrayList<>();

        while (true) {
            System.out.println("-------login-------");
            System.out.println("欢迎来到文字格斗游戏");
            System.out.println("-------login-------");
            System.out.println("请选择登录方式：");
            System.out.println("1.登录");
            System.out.println("2.注册");
            System.out.println("3.退出\n");

            Scanner sc = new Scanner(System.in);
            String choice = sc.next();
            switch (choice) {
                case "1":
                    login(list);
                    break;
                case "2":
                    register(list);
                    break;
                case "3":
                    System.exit(0);
                    break;
                default:
                    System.out.println("输入有误，请重新输入");
                    break;
            }
        }
    }
    public void register(ArrayList<user>List){
        System.out.println("用户选择了注册");
        user u = new user();
        Scanner sc = new Scanner(System.in);

        while(true) {
            System.out.print("请输入姓名:");
            String name = sc.next();
            System.out.println();

            if (!checkname(name)) {
                System.out.println("用户名只能是字母数字组合，长度3~16");
                continue;
            }
            if(Iscontain(name,List)){
                System.out.println("用户名已经存在");
                continue;
            }
            System.out.print("请输入密码:");
            String password = sc.next();
            if (!checkpassword(password))
            {
                System.out.println("密码只能是字母数字组合3~8");
                continue;
            }


            u.setName(name);
            u.setPassword(password);
            List.add(u);
            System.out.println("注册成功");
            break;

        }

    }
    public void login(ArrayList<user>List){
        System.out.println("用户选择了登录");
        Scanner sc = new Scanner(System.in);
        generatecode c = new generatecode();
        int cnt = 3;
        while (cnt>0) {

            System.out.print("请输入用户名：");
            String name = sc.next();
            if(!Iscontain(name,List)){
                System.out.println("用户未注册，请重新输入");
                break;
            }
            if(Islock(name,List)) {
                System.out.printf("%s已经锁定，请联系管理员1111-1111%n", name);
                continue;
            }

            System.out.print("请输入密码：");
            String password = sc.next();

            String checkcode=c.generate();
            System.out.print("请输入验证码:"+checkcode+"  验证码: ");
            String code = sc.next();
            if(code.equals(checkcode))
            {
                if(Isright(name,password,List)){
                    System.out.println("登录成功");
                    //
                    Fightinggame g = new Fightinggame();
                    g.gameStart(name);
                    break;
                }else{
                    System.out.println("密码错误");
                    cnt--;
                    if(cnt==0){
                        lock(name,List);
                        System.out.println("此账号以封号");
                    }
                }
            }else{
                System.out.println("验证码错误，请重试");
            }


        }


    }
    public boolean Iscontain(String name,ArrayList<user>List){
        for (user user : List) if (name.equals(user.getName())) return true;
        return false;
    }
    public boolean checkname(String str){

        return str.matches("(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]{3,16}");

    }
    public boolean checkpassword(String str){

        return str.matches("(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9]{3,8}");

    }
    public boolean Islock(String name,ArrayList<user>List){
        for (user user : List)
            if (name.equals(user.getName()) && user.getStatus())
                return false;
        return true;

    }
    public boolean Isright(String name,String password,ArrayList<user>List){
        for (user user : List) if (name.equals(user.getName())){
            if(user.getPassword().equals(password)){
                return true;
            }
        }
        return false;
    }
    public void lock(String name,ArrayList<user>List){
        for (user user : List) if (name.equals(user.getName())){
            user.setStatus(false);
        }
    }
}
