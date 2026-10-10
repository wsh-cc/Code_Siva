package FightingGame.src.Bean;

import java.util.ArrayList;

public class HeroCharacter extends Character {
    public ArrayList<String>SKILLS;

    public HeroCharacter() {
            SKILLS = new ArrayList<String>();
    }

    public HeroCharacter(int DEF, int ATK, int HP, String NAME) {
        super(DEF, ATK, HP, NAME);
        SKILLS = new ArrayList<>();
    }
    public String showSKILLS() {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < SKILLS.size(); i++) {
            sb.append(SKILLS.get(i));
            if(i != SKILLS.size()-1){
                sb.append(",");
            }
        }
        return sb.toString();
    }
}
