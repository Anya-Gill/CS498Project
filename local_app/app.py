from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Allows the frontend to talk to this server
VM_BASE_URL = "http://34.70.223.177:8080"


# get top 10 most retweeted original tweets
@app.route("/endpoint-one", methods=["GET"])
def endpoint_one():
    """
    Proxies to the VM Flask server's first endpoint.
    Replace ADD_ENDPOINT_ONE with the actual endpoint path on the VM server.
    """
    try:
        response = requests.get(f"{VM_BASE_URL}/top-retweeted")
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not connect to the VM Flask server."}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"VM server returned an error: {str(e)}"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/endpoint-two", methods=["GET"])
def endpoint_two():
    """
    Proxies to the VM Flask server's second endpoint.
    Replace ADD_ENDPOINT_TWO with the actual endpoint path on the VM server.
    """
    try:
        response = requests.get(f"{VM_BASE_URL}/ADD_ENDPOINT_TWO")
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not connect to the VM Flask server."}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"VM server returned an error: {str(e)}"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/ping", methods=["GET"])
def ping():
    """
    Proxies to the VM Flask server's ping endpoint.
    Returns a status check and a single raw sample tweet row.
    Replace ADD_PING_ENDPOINT with the actual ping path on the VM server (e.g. /ping).
    """
    try:
        response = requests.get(f"{VM_BASE_URL}/ping")
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not connect to the VM Flask server."}), 503
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": f"VM server returned an error: {str(e)}"}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
