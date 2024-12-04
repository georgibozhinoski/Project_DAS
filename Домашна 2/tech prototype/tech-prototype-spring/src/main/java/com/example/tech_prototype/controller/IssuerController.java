package com.example.tech_prototype.controller;

import com.example.tech_prototype.model.Issuer;
import com.example.tech_prototype.repository.IssuerRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/issuers")
@CrossOrigin(origins = "http://localhost:3000")  // Allow requests from React app
public class IssuerController {

    @Autowired
    private IssuerRepository issuerRepository;

    // Get all issuers
    @GetMapping
    public List<Issuer> getAllIssuers() {
        return issuerRepository.findAll();
    }

    // Get an issuer by ID
    @GetMapping("/{id}")
    public Optional<Issuer> getIssuerById(@PathVariable Long id) {
        return issuerRepository.findById(id);
    }

    // Create a new issuer
    @PostMapping
    public Issuer createIssuer(@RequestBody Issuer issuer) {
        return issuerRepository.save(issuer);
    }

    // Update an existing issuer
    @PutMapping("/{id}")
    public Issuer updateIssuer(@PathVariable Long id, @RequestBody Issuer issuer) {
        // Ensure the issuer exists in the database before updating
        return issuerRepository.findById(id)
                .map(existingIssuer -> {
                    existingIssuer.setCode(issuer.getCode());
                    existingIssuer.setName(issuer.getName());
                    return issuerRepository.save(existingIssuer);
                })
                .orElseGet(() -> {
                    issuer.setId(id);
                    return issuerRepository.save(issuer);
                });
    }

    // Delete an issuer by ID
    @DeleteMapping("/{id}")
    public void deleteIssuer(@PathVariable Long id) {
        issuerRepository.deleteById(id);
    }
}
