package FightingGame.src.Bean;

import java.util.ArrayList;

public class Character {
    public String NAME;
    public int HP;
    public int MAXHP;
    public int ATK;
    public int DEF;

    public Character() {
    }

    public Character( int DEF, int ATK, int HP, String NAME) {
        this.DEF = DEF;
        this.ATK = ATK;
        this.HP = HP;
        this.MAXHP = HP;
        this.NAME = NAME;
    }

    public boolean IsAlive(){
        return this.HP >0;
    }

    public void Heal(int healvalue){
        this.HP = Math.min(this.HP + healvalue, MAXHP);
    }

    public int takeDamage(int damagevalue) {
       int damage = this.DEF > damagevalue ? 1 : damagevalue-this.DEF;
       this.HP -= damage;
       if(this.HP < 0)this.HP = 0;
       return damage;
    }
    public void show()
    {
        System.out.println(this.NAME+": [HP:"+this.HP+" ATK:"+this.ATK+" DEF:"+this.DEF+"]");
    }
}
