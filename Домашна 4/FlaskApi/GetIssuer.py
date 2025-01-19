from flask import *
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

SPRING_API_URL = "http://localhost:8080/api/issuers"

@app.route("/fetch_issuers", methods=["GET"])
def fetch_issuers():
    url = "https://www.mse.mk/en/stats/symbolhistory/kmb"

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        issuers = []
        for option in soup.select("#Code option"):
            code = option.get("value")
            name = option.text.strip()

            if not any(char.isdigit() for char in code) and not any(char.isdigit() for char in name):
                issuers.append({"code": code, "name": name})

        response = requests.post(SPRING_API_URL, json=issuers)

        if response.status_code == 200:
            return jsonify({"message": "Issuers fetched and stored successfully in H2."}), 200
        else:
            return jsonify({"error": "Failed to store issuers in Spring API."}), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch data from the website: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
