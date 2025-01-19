package com.mse.mse_webapp.repository;

import com.mse.mse_webapp.model.Signal;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface SignalRepository extends JpaRepository<Signal, Long> {

}
