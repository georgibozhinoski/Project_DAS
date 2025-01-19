import React, { useEffect, useState } from "react";

const List = () => {
    const [state, setState] = useState([]);

    useEffect(() => {
        fetch("http://localhost:8080/api/issuers")
            .then((response) => response.json())
            .then((data) => {
                setState(data);
            })
            .catch((error) => console.error("Error fetching data:", error));
    }, []);

    return (
        <div>
            <h1>Issuer List</h1>
            {state.length > 0 ? (
                <ul>
                    {state.map((issuer) => (
                        <li key={issuer.id}>
                            <strong>Code:</strong> {issuer.code}, <strong>Name:</strong> {issuer.name}
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No data found.</p>
            )}
        </div>
    );
};

export default List;
