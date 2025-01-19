package com.mse.mse_webapp.repository;

import com.mse.mse_webapp.model.Issuer;
import org.springframework.data.jpa.repository.JpaRepository;

public interface IssuerRepository extends JpaRepository<Issuer, Long> {
    Issuer findByCode(String code);
}
