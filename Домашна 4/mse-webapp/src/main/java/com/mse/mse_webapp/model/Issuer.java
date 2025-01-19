package com.mse.mse_webapp.model;

import jakarta.persistence.*;

@Entity
@Table(name = "issuers")
public class Issuer {

    @Id
    @Column(name = "code")
    private String code;

    @Column(name = "name", nullable = false)
    private String name;

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    @Override
    public String toString() {
        return "Issuer{" +
                "code='" + code + '\'' +
                ", name='" + name + '\'' +
                '}';
    }
}
