package com.example.tech_prototype.service;

import com.example.tech_prototype.model.HistoricalData;
import com.example.tech_prototype.repository.HistoricalDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class HistoricalDataServiceImpl implements HistoricalDataService {

    private final HistoricalDataRepository historicalDataRepository;

    @Autowired
    public HistoricalDataServiceImpl(HistoricalDataRepository historicalDataRepository) {
        this.historicalDataRepository = historicalDataRepository;
    }

    @Override
    public List<HistoricalData> findAll() {
        return historicalDataRepository.findAll();
    }

    @Override
    public HistoricalData findById(Long id) {
        return historicalDataRepository.findById(id).orElse(null);
    }

    @Override
    public HistoricalData save(HistoricalData historicalData) {
        return historicalDataRepository.save(historicalData);
    }

    @Override
    public void deleteById(Long id) {
        historicalDataRepository.deleteById(id);
    }
}
