package com.mse.mse_webapp.model;

import jakarta.persistence.*;
import java.time.LocalDate;

@Entity
@Table(name = "signals")
public class Signal {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "issuer_code", nullable = false)
    private String issuerCode;

    @Column(name = "timeframe", nullable = false)
    private String timeframe;

    @Column(name = "signal", nullable = false)
    private String signal;

    @Column(name = "date", nullable = false)
    private LocalDate date;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getIssuerCode() {
        return issuerCode;
    }

    public void setIssuerCode(String issuerCode) {
        this.issuerCode = issuerCode;
    }

    public String getTimeframe() {
        return timeframe;
    }

    public void setTimeframe(String timeframe) {
        this.timeframe = timeframe;
    }

    public String getSignal() {
        return signal;
    }

    public void setSignal(String signal) {
        this.signal = signal;
    }

    public LocalDate getDate() {
        return date;
    }

    public void setDate(LocalDate date) {
        this.date = date;
    }

    @Override
    public String toString() {
        return "Signal{" +
                "id=" + id +
                ", issuerCode='" + issuerCode + '\'' +
                ", timeframe='" + timeframe + '\'' +
                ", signal='" + signal + '\'' +
                ", date=" + date +
                '}';
    }
}
