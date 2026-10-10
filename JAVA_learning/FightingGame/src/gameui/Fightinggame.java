package FightingGame.src.gameui;

import FightingGame.src.Bean.Character;
import FightingGame.src.Bean.EnemyCharacter;
import FightingGame.src.Bean.HeroCharacter;

import java.util.ArrayList;
import java.util.Random;
import java.util.Scanner;

public class Fightinggame {
    public void gameStart(String username){
        System.out.println("******欢迎来到文字格斗游戏"+username+"*****");
        HeroCharacter hero = creatPlayer(username);
        hero.SKILLS.add("普通攻击");
        hero.SKILLS.add("强力一击");
        hero.SKILLS.add("生命汲取");


        System.out.println("创建成功");
        System.out.print("初始属性为:");
        hero.show();
        System.out.println("初始技能为:"+hero.showSKILLS());

        ArrayList<EnemyCharacter>enemyList = new ArrayList<EnemyCharacter>();
        enemyList.add(new EnemyCharacter(10,15,80,"初级战士","猛击"));
        enemyList.add(new EnemyCharacter(5,20,60,"敏捷刺客","快速攻击"));
        enemyList.add(new EnemyCharacter(20,10,120,"重装坦克","防御姿态"));
        enemyList.add(new EnemyCharacter(8,25,70,"神秘法师","火球术"));

        int cnt = 1;
        while(hero.IsAlive()){


            if(cnt>1){
                for (int i = 0; i < 4; i++) {
                    enemyList.get(i).HP+=10;
                    enemyList.get(i).ATK+=3;
                    enemyList.get(i).DEF+=2;

                }
            }

            Random r= new Random();
            EnemyCharacter Enemy = enemyList.get(r.nextInt(0,4));
            EnemyCharacter enemy = new EnemyCharacter(Enemy.DEF, Enemy.ATK, Enemy.HP, Enemy.NAME, Enemy.SKILL);
            System.out.println("-------战斗开始--------");
            int round =1;
            while (hero.IsAlive()) {
                System.out.println("第"+round+"回合开始");
                showHP(enemy.NAME, enemy.HP, enemy.MAXHP);

                showHP(hero.NAME,hero.HP,hero.MAXHP);

                heroturn(hero,enemy);
//                showHP(enemy.NAME, enemy.HP, enemy.MAXHP);
//                showHP(hero.NAME,hero.HP,hero.MAXHP);
                if(!enemy.IsAlive()){
                    System.out.println("victory");
                   if(cnt%3==0) {
                       System.out.println("------level up------");
                       System.out.println("MAXHP:"+hero.MAXHP+"->\t"+hero.MAXHP+"+"+5);
                       System.out.println("ATK:"+hero.ATK+"->\t"+hero.ATK+"+"+3);
                       System.out.println("DEF:"+hero.DEF+"->\t"+hero.DEF+"+"+5);

                       hero.MAXHP+=5;
                       hero.HP+=5;
                       hero.ATK+=3;
                       hero.DEF+=2;
                   }
                    int re = r.nextInt(20,41);
                    hero.Heal(re);
                    System.out.println("your life recovery"+re+"HP");
//                    showHP(hero.NAME,hero.HP,hero.MAXHP);
                    System.out.println("continue game? yes/no");
                    Scanner sc = new Scanner(System.in);
                    if(sc.nextLine()=="no")return;////////////////////////////
                    else break;

                }
                if(!hero.IsAlive()){
                    break;
                }

//                System.out.println("怪物回合");
                enemyturn(hero,enemy);
              // showHP(enemy.NAME, enemy.HP, enemy.MAXHP);
               // showHP(hero.NAME,hero.HP,hero.MAXHP);
                if(!hero.IsAlive()){
                    break;
                }
//                System.exit(0);
                round++;
            }

            cnt+=1;
        }
        System.out.println("you die");

    }
    public HeroCharacter creatPlayer(String username){
        System.out.println("创建您的角色：");
        System.out.println("您的角色名是: " +username);

        int points =20;
        Scanner sc = new Scanner(System.in);
        int[] values =new int[3];
        String[] attributes = {"生命值","攻击力","防御值"};

        while(true){
            System.out.println("请分配属性点(20点)");
            System.out.println("1.生命值(每点+ 10  HP)");
            System.out.println("2.攻击力(每点+ 2  ATK)");
            System.out.println("3.防御值(每点+ 10 DEF)");
            for(int i=0;i<3;i++)
            {
                System.out.print("请输入"+attributes[i]+"属性加点：");
                int Setpoint = sc.nextInt();
                values[i] = Setpoint;
            }
            if((values[0]+values[1]+values[2]==20)&&(values[0]>0&&values[1]>0&&values[2]>0)){

                return new HeroCharacter(
                        10*values[2],
                        10+2*values[1],
                        100+10*values[0],
                        username);
            }
            else{
                System.out.println("输入有误,请重新输入");
            }
        }
    }
    public void showHP(String name , int hp,int maxhp){
        //        System.out.println("[████████████████████] 100/100 HP");
        int len = 20;
        int fillhp = (int)((hp*1.0/maxhp)*len);
        StringBuilder sb = new StringBuilder();
        sb.append(name).append(": [");
        for (int i = 0; i < 20; i++) {
           if (i<fillhp)
               sb.append("█");
           else sb.append(" ");
        }

       sb.append("]").append(hp).append("/").append(maxhp).append(" HP");
        System.out.println(sb.toString());
    }
    public void heroturn(HeroCharacter hero,EnemyCharacter enemy)
    {
        System.out.println("----玩家回合----");
        System.out.println("1.普通攻击");
        System.out.println("2.强力攻击");
        System.out.println("3.生命汲取");
        System.out.println("请选择行动（1-3）");
        Scanner sc = new Scanner(System.in);
        switch (sc.nextLine())
        {default:
            System.out.println("没有这个操作默认普通攻击");
            case "1":
                System.out.println("1.普通攻击");

                System.out.println("你对"+enemy.NAME+"使用了普通攻击造成了"+ enemy.takeDamage(hero.ATK)+"点攻击");
                break;
                case "2":
                    System.out.println("2.强力攻击");

                    hero.takeDamage(hero.DEF+10);
                    System.out.println("你消耗10点HP"+enemy.NAME+"使用了强力一击造成了"+enemy.takeDamage((int)(hero.ATK*1.8))+"点攻击");

                    break;
                    case "3":
                        System.out.println("3.生命汲取");
                        Random r = new Random();
                        int h = r.nextInt(0,21);
                        System.out.println("你使用生命汲取恢复了"+h+"点HP");

                        hero.Heal(h);
                        break;
        }

    }
    public void enemyturn(HeroCharacter hero,EnemyCharacter enemy)
    {

        Random r = new Random();
        int status = r.nextInt(10);

        if (status < 7) {

            System.out.println("monster use a simple atk , you have decreased "+ hero.takeDamage(enemy.ATK)+" HP");
        }else{
            switch (enemy.SKILL) {
                case "猛击" :

                    System.out.println("enemy use skill "+enemy.SKILL+" caused "+hero.takeDamage((int)(enemy.ATK*1.5))+" damage");
                    break;
                case "快速攻击":

                    hero.takeDamage((int)(enemy.ATK*0.6));
                    System.out.println("enemy use skill "+enemy.SKILL+" caused all "+hero.takeDamage((int)(enemy.ATK*0.6))+"*2 damage");

                    break;
                case "防御姿态":
                    enemy.defending=true;
                    System.out.println("enemy use skill "+enemy.SKILL+" caused "+0+" damage");

                    break;
                case "火球术":

                    System.out.println("enemy use skill "+enemy.SKILL+" caused "+ hero.takeDamage((int)(enemy.ATK*1.8))+" damage");

                    break;
                    default:break;
            }
        }


    }
}
