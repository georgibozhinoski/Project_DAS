package com.example.tech_prototype.controller;

import com.example.tech_prototype.model.HistoricalData;
import com.example.tech_prototype.service.HistoricalDataService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/historical-data")
@CrossOrigin(origins = "http://localhost:3000")  // Allow requests from React app
public class HistoricalDataController {

    private final HistoricalDataService historicalDataService;

    @Autowired
    public HistoricalDataController(HistoricalDataService historicalDataService) {
        this.historicalDataService = historicalDataService;
    }

    @GetMapping
    public List<HistoricalData> getAllHistoricalData() {
        return historicalDataService.findAll();
    }

    @GetMapping("/{id}")
    public HistoricalData getHistoricalDataById(@PathVariable Long id) {
        return historicalDataService.findById(id);
    }

    @PostMapping
    public HistoricalData createHistoricalData(@RequestBody HistoricalData historicalData) {
        return historicalDataService.save(historicalData);
    }

    @PutMapping("/{id}")
    public HistoricalData updateHistoricalData(@PathVariable Long id, @RequestBody HistoricalData historicalData) {
        return historicalDataService.findById(id) != null
                ? historicalDataService.save(historicalData)
                : null;
    }

    @DeleteMapping("/{id}")
    public void deleteHistoricalData(@PathVariable Long id) {
        historicalDataService.deleteById(id);
    }
}
