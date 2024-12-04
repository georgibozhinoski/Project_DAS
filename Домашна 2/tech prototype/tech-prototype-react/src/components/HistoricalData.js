// src/components/HistoricalData.js
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Container, Button } from '@mui/material';

const HistoricalData = () => {
    const [historicalData, setHistoricalData] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8080/api/historical-data')  // Adjust the API URL as needed
            .then(response => response.json())
            .then(data => setHistoricalData(data));
    }, []);

    return (
        <Container style={{ paddingTop: '20px' }}>
            <h1>Historical Data</h1>
            <TableContainer component={Paper} style={{ maxHeight: 400, overflow: 'auto' }}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>Issuer Code</TableCell>
                            <TableCell>Date</TableCell>
                            <TableCell>Last Price</TableCell>
                            <TableCell>Max Price</TableCell>
                            <TableCell>Min Price</TableCell>
                            <TableCell>Average Price</TableCell>
                            <TableCell>Quantity</TableCell>
                            <TableCell>Turnover Best</TableCell>
                            <TableCell>Total Turnover</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {historicalData.map((data) => (
                            <TableRow key={data.id}>
                                <TableCell>{data.id}</TableCell>
                                <TableCell>{data.issuerCode}</TableCell>
                                <TableCell>{data.date}</TableCell>
                                <TableCell>{data.lastPrice}</TableCell>
                                <TableCell>{data.maxPrice}</TableCell>
                                <TableCell>{data.minPrice}</TableCell>
                                <TableCell>{data.avgPrice}</TableCell>
                                <TableCell>{data.quantity}</TableCell>
                                <TableCell>{data.turnoverBest}</TableCell>
                                <TableCell>{data.totalTurnover}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
            <Link to="/">
                <Button variant="contained" color="primary" style={{ marginTop: '20px' }}>
                    Back to Home
                </Button>
            </Link>
        </Container>
    );
};

export default HistoricalData;
