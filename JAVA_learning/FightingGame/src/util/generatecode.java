package FightingGame.src.util;

import java.util.Random;

public class generatecode
{
    public String generate(){
        String ss = "0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLXCVBNM";
        StringBuilder sb = new StringBuilder();
        Random r = new Random();
        for (int i = 0; i < 5; i++) {

            int n = r.nextInt(ss.length());
            sb.append(ss.charAt(n));
        }
        return sb.toString();
    }
}
