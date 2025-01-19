package com.mse.mse_webapp.repository;

import com.mse.mse_webapp.model.HistoricalData;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface HistoricalDataRepository extends JpaRepository<HistoricalData, Long> {


    List<HistoricalData> findByIssuerCode(String issuerCode);
}
