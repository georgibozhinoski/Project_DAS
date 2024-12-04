
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppBar, Toolbar, Button, Typography } from '@mui/material';
import Home from './components/Home';
import IssuerCodes from './components/IssuerCodes';
import HistoricalData from './components/HistoricalData';

const App = () => {
    return (
        <Router>
            <div style={{ backgroundColor: '#f4f6f8', minHeight: '100vh' }}>
                {/* Navigation Bar */}
                <AppBar position="static" style={{ backgroundColor: '#3f51b5' }}>
                    <Toolbar>
                        <Typography variant="h6" style={{ flexGrow: 1 }}>
                            Tech Prototype
                        </Typography>
                        <Button color="inherit" href="/">Home</Button>
                        <Button color="inherit" href="/issuer-codes">Issuer Codes</Button>
                        <Button color="inherit" href="/historical-data">Historical Data</Button>
                    </Toolbar>
                </AppBar>

                {/* Routes */}
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/issuer-codes" element={<IssuerCodes />} />
                    <Route path="/historical-data" element={<HistoricalData />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
