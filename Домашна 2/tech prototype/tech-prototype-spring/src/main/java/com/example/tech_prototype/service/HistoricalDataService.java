package com.example.tech_prototype.service;

import com.example.tech_prototype.model.HistoricalData;

import java.util.List;

public interface HistoricalDataService {
    List<HistoricalData> findAll();
    HistoricalData findById(Long id);
    HistoricalData save(HistoricalData historicalData);
    void deleteById(Long id);
}
