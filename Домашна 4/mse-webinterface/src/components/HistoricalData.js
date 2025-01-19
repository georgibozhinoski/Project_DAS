import React, { useState } from "react";
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Container,
    Button,
    TablePagination,
} from "@mui/material";

const HistoricalData = () => {
    const [historicalData, setHistoricalData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10); // Rows per page

    const fetchHistoricalData = async () => {
        setLoading(true);
        try {
            const response = await fetch("http://localhost:8080/api/historicaldata");
            const data = await response.json();
            setHistoricalData(data);
        } catch (error) {
            console.error("Error fetching historical data:", error);
            alert("Failed to fetch historical data. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    return (
        <Container style={{ paddingTop: "20px" }}>
            <h1>Historical Data</h1>
            <Button
                variant="contained"
                color="primary"
                onClick={fetchHistoricalData}
                disabled={loading}
            >
                {loading ? "Fetching Data..." : "Fetch Historical Data"}
            </Button>
            {historicalData.length > 0 && (
                <TableContainer
                    component={Paper}
                    style={{ marginTop: "20px", maxHeight: 600 }}
                >
                    <Table stickyHeader>
                        <TableHead>
                            <TableRow>
                                <TableCell>ID</TableCell>
                                <TableCell>Issuer Code</TableCell>
                                <TableCell>Date</TableCell>
                                <TableCell>Last Price</TableCell>
                                <TableCell>Max Price</TableCell>
                                <TableCell>Min Price</TableCell>
                                <TableCell>Average Price</TableCell>
                                <TableCell>Percent Change</TableCell>
                                <TableCell>Quantity</TableCell>
                                <TableCell>Turnover Best</TableCell>
                                <TableCell>Total Turnover</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {historicalData
                                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage) // Slice data for pagination
                                .map((data) => (
                                    <TableRow key={data.id}>
                                        <TableCell>{data.id}</TableCell>
                                        <TableCell>{data.issuerCode}</TableCell>
                                        <TableCell>{data.date}</TableCell>
                                        <TableCell>{data.lastPrice}</TableCell>
                                        <TableCell>{data.maxPrice}</TableCell>
                                        <TableCell>{data.minPrice}</TableCell>
                                        <TableCell>{data.avgPrice}</TableCell>
                                        <TableCell>{data.percentChange}</TableCell>
                                        <TableCell>{data.quantity}</TableCell>
                                        <TableCell>{data.turnoverBest}</TableCell>
                                        <TableCell>{data.totalTurnover}</TableCell>
                                    </TableRow>
                                ))}
                        </TableBody>
                    </Table>
                    <TablePagination
                        rowsPerPageOptions={[10, 25, 50, 100]}
                        component="div"
                        count={historicalData.length}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={handleChangePage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                    />
                </TableContainer>
            )}
        </Container>
    );
};

export default HistoricalData;
