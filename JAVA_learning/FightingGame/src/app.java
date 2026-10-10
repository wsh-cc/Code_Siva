package FightingGame.src;

import FightingGame.src.gameui.Fightinggame;
import FightingGame.src.gameui.Login;

public class app {
    public static void main(String[] args) {
        Login l = new Login();
        l.start();

        Fightinggame g = new Fightinggame();
        g.gameStart(" test");
    }
}

