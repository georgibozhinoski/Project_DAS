package com.example.tech_prototype.model;

import jakarta.persistence.*;

@Entity
@Table(name = "historical_data")
public class HistoricalData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "issuer_code", nullable = false)
    private String issuerCode;

    @Column(name = "date", nullable = false)
    private String date;

    @Column(name = "last_price")
    private String lastPrice;

    @Column(name = "max_price")
    private String maxPrice;

    @Column(name = "min_price")
    private String minPrice;

    @Column(name = "avg_price")
    private String avgPrice;

    @Column(name = "percent_change")
    private String percentChange;

    @Column(name = "quantity")
    private String quantity;

    @Column(name = "turnover_best")
    private String turnoverBest;

    @Column(name = "total_turnover")
    private String totalTurnover;

    // Getters and Setters
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

    public String getDate() {
        return date;
    }

    public void setDate(String date) {
        this.date = date;
    }

    public String getLastPrice() {
        return lastPrice;
    }

    public void setLastPrice(String lastPrice) {
        this.lastPrice = lastPrice;
    }

    public String getMaxPrice() {
        return maxPrice;
    }

    public void setMaxPrice(String maxPrice) {
        this.maxPrice = maxPrice;
    }

    public String getMinPrice() {
        return minPrice;
    }

    public void setMinPrice(String minPrice) {
        this.minPrice = minPrice;
    }

    public String getAvgPrice() {
        return avgPrice;
    }

    public void setAvgPrice(String avgPrice) {
        this.avgPrice = avgPrice;
    }

    public String getPercentChange() {
        return percentChange;
    }

    public void setPercentChange(String percentChange) {
        this.percentChange = percentChange;
    }

    public String getQuantity() {
        return quantity;
    }

    public void setQuantity(String quantity) {
        this.quantity = quantity;
    }

    public String getTurnoverBest() {
        return turnoverBest;
    }

    public void setTurnoverBest(String turnoverBest) {
        this.turnoverBest = turnoverBest;
    }

    public String getTotalTurnover() {
        return totalTurnover;
    }

    public void setTotalTurnover(String totalTurnover) {
        this.totalTurnover = totalTurnover;
    }
}
