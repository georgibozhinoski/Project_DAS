package com.example.tech_prototype.repository;

import com.example.tech_prototype.model.Issuer;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface IssuerRepository extends JpaRepository<Issuer, Long> {
    // No need to define custom methods unless necessary (e.g., findByCode, etc.)
}
