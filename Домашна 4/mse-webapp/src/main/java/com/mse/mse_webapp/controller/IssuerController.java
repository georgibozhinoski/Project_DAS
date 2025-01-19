package com.mse.mse_webapp.controller;

import com.mse.mse_webapp.model.Issuer;
import com.mse.mse_webapp.repository.IssuerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/issuers")
public class IssuerController {

    @Autowired
    private IssuerRepository issuerRepository;

    @PostMapping
    public String addIssuers(@RequestBody List<Issuer> issuers) {
        try {
            issuerRepository.saveAll(issuers);
            return "Issuers saved successfully!";
        } catch (Exception e) {
            return "Failed to save issuers: " + e.getMessage();
        }
    }

    @GetMapping
    public List<Issuer> getAllIssuers() {
        try {
            return issuerRepository.findAll();
        } catch (Exception e) {
            return null;
        }
    }
}
