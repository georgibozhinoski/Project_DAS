package com.mse.mse_webapp.controller;

import com.mse.mse_webapp.model.Signal;
import com.mse.mse_webapp.repository.SignalRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/signals")
public class SignalController {

    @Autowired
    private SignalRepository signalRepository;

    @PostMapping("/add")
    public String addSignals(@RequestBody List<Signal> signalList) {
        try {
            signalRepository.saveAll(signalList);
            return "Signals saved successfully!";
        } catch (Exception e) {
            return "Failed to save signals: " + e.getMessage();
        }
    }

    @GetMapping
    public List<Signal> getAllSignals() {
        try {
            return signalRepository.findAll();
        } catch (Exception e) {
            throw new RuntimeException("Failed to retrieve signals: " + e.getMessage());
        }
    }
}
