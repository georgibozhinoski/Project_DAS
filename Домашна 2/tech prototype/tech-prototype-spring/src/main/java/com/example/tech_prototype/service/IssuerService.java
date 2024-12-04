package com.example.tech_prototype.service;

import com.example.tech_prototype.model.Issuer;

import java.util.List;

public interface IssuerService {
    List<Issuer> findAll();
    Issuer findById(Long id);
    Issuer save(Issuer issuer);
}
