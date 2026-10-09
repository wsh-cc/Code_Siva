package FightingGame.src.Bean;

import java.util.Random;

public class user {
    private String id;
    private String name;
    private String password;    
    private boolean status;

    public user() {
        this.id = setId();
        this.status = true;
    }

    public user(String name,String password) {
        this.password = password;
        this.name = name;

        this.id = setId();
        this.status = true;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getPassword() {
        return password;
    }

    public boolean getStatus() {
        return status;
    }

    private String setId() {
        StringBuilder sb = new StringBuilder("heima");
        Random r = new Random();
        for (int i = 0; i < 5; i++) {
            sb.append(r.nextInt(0,10));
        }
        return sb.toString();
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void setStatus(boolean status) {
        this.status = status;
    }
}
