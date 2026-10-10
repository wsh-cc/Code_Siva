package FightingGame.src.Bean;

public class EnemyCharacter extends Character{
    public String SKILL;
    public boolean defending;

    public EnemyCharacter() {
        this.defending = false;
    }

    public EnemyCharacter(int DEF, int ATK, int HP, String NAME,String SKILL) {
        super(DEF, ATK, HP, NAME);
        this.SKILL=SKILL;
        this.defending = false;

    }
    @Override
    public int takeDamage(int damagevalue) {
        if(defending){
            damagevalue = Math.max(damagevalue / 2, 1);
            defending=false;

        }
        return super.takeDamage(damagevalue);
    }
    @Override
    public void show()
    {
        System.out.print("怪物: ");
        super.show();
    }
}
