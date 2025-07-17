from flask import Flask, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Configura logging para Render
logging.basicConfig(level=logging.INFO)

# Variables de entorno
CLIENT_ID = os.getenv("BPD_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("BPD_CLIENT_SECRET", "")

# Función para obtener token OAuth2
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

    logging.info("Solicitando token al BPD...")
    r = requests.post(url, headers=headers, data=data, timeout=10)
    r.raise_for_status()
    token = r.json().get("access_token")
    if not token:
        raise Exception("Token no encontrado en respuesta")
    return token

# Función para consultar tasa
def consultar_tasa(token):
    url = "https://apiqa.bpd.com.do:8243/bpd/consulta-tasa/v1/tasa"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    logging.info("Consultando tasa...")
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()

# Endpoint raíz para probar si la API está viva
@app.route("/", methods=["GET"])
def index():
    return jsonify({"mensaje": "API de tasa BPD activa"}), 200

# Endpoint principal
@app.route("/tasa", methods=["GET"])
def endpoint_tasa():
    try:
        token = obtener_token()
        datos = consultar_tasa(token)
        return jsonify(datos)
    except requests.exceptions.Timeout:
        logging.error("Tiempo de espera excedido")
        return jsonify({"error": "Tiempo de espera excedido"}), 504
    except requests.exceptions.ConnectionError:
        logging.error("Error de conexión con el servidor BPD")
        return jsonify({"error": "No se pudo conectar al servidor del BPD"}), 502
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error: {http_err}")
        return jsonify({"error": f"HTTP error: {str(http_err)}"}), 401
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
