// src/components/Home.js
import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Container, Typography } from '@mui/material';

const Home = () => {
    return (
        <Container style={{ paddingTop: '20px', textAlign: 'center' }}>
            <Typography variant="h3" gutterBottom>
                Data for the Macedonian Stock Exchange
            </Typography>
            <Button variant="contained" color="primary" style={{ margin: '10px' }} component={Link} to="/issuer-codes">
                Issuer Codes
            </Button>
            <Button variant="contained" color="secondary" style={{ margin: '10px' }} component={Link} to="/historical-data">
                Historical Data
            </Button>
        </Container>
    );
};

export default Home;
