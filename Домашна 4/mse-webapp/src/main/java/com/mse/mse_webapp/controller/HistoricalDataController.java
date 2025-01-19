package com.mse.mse_webapp.controller;

import com.mse.mse_webapp.model.HistoricalData;
import com.mse.mse_webapp.repository.HistoricalDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/historicaldata")
public class HistoricalDataController {

    @Autowired
    private HistoricalDataRepository historicalDataRepository;

    @PostMapping
    public String addHistoricalData(@RequestBody List<HistoricalData> historicalDataList) {
        try {
            historicalDataRepository.saveAll(historicalDataList);
            return "Historical data saved successfully!";
        } catch (Exception e) {
            return "Failed to save historical data: " + e.getMessage();
        }
    }

    @GetMapping
    public List<HistoricalData> getAllHistoricalData() {
        try {
            return historicalDataRepository.findAll();
        } catch (Exception e) {
            throw new RuntimeException("Failed to retrieve historical data: " + e.getMessage());
        }
    }

    @GetMapping("/byIssuer")
    public List<HistoricalData> getHistoricalDataByIssuer(@RequestParam String issuerCode) {
        try {
            return historicalDataRepository.findByIssuerCode(issuerCode);
        } catch (Exception e) {
            throw new RuntimeException("Failed to retrieve historical data for issuer " + issuerCode + ": " + e.getMessage());
        }
    }
}
