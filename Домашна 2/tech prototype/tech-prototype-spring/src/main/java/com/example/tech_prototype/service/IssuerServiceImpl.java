package com.example.tech_prototype.service;
import com.example.tech_prototype.model.Issuer;
import com.example.tech_prototype.repository.IssuerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class IssuerServiceImpl implements IssuerService {

    private final IssuerRepository issuerRepository;

    @Autowired
    public IssuerServiceImpl(IssuerRepository issuerRepository) {
        this.issuerRepository = issuerRepository;
    }

    @Override
    public List<Issuer> findAll() {
        return issuerRepository.findAll();
    }

    @Override
    public Issuer findById(Long id) {
        return issuerRepository.findById(id).orElse(null);
    }

    @Override
    public Issuer save(Issuer issuer) {
        return issuerRepository.save(issuer);
    }
}
