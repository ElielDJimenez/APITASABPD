
from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

# Configura tus credenciales como variables de entorno o reemplaza directamente
CLIENT_ID = os.getenv("BPD_CLIENT_ID", "TU_CLIENT_ID")
CLIENT_SECRET = os.getenv("BPD_CLIENT_SECRET", "TU_CLIENT_SECRET")

def obtener_token():
    url = "https://apiqa.bpd.com.do:8243/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    r = requests.post(url, headers=headers, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

def consultar_tasa(token):
    url = "https://apiqa.bpd.com.do:8243/bpd/consulta-tasa/v1/tasa"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

@app.route('/tasa', methods=['GET'])
def endpoint_tasa():
    try:
        token = obtener_token()
        datos = consultar_tasa(token)
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
