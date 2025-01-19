// src/components/IssuerCodes.js
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Button, Container } from '@mui/material'; // Import Button here

const IssuerCodes = () => {
    const [issuers, setIssuers] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8080/api/issuers')  // Adjust the API URL as needed
            .then(response => response.json())
            .then(data => setIssuers(data));
    }, []);

    return (
        <Container style={{ paddingTop: '20px' }}>
            <h1>Issuer Codes</h1>
            <TableContainer component={Paper} style={{ maxHeight: 400, overflow: 'auto' }}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>ID</TableCell>
                            <TableCell>Code</TableCell>
                            <TableCell>Name</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {issuers.map((issuer) => (
                            <TableRow key={issuer.id}>
                                <TableCell>{issuer.id}</TableCell>
                                <TableCell>{issuer.code}</TableCell>
                                <TableCell>{issuer.name}</TableCell>
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

export default IssuerCodes;
