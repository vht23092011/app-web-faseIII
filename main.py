from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_url_path="", static_folder=".")

API_KEY = os.getenv("IBM_API_KEY")
API_KEY = os.getenv("DEPLOYMENT_URL")


def obtener_token():
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "apikey": API_KEY,
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    return response.json()["access_token"]


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/predict", methods=["POST"])
def predecir():
    datos = request.get_json()
    if not datos or "values" not in datos or not datos["values"]:
        return jsonify({"error": "Datos inválidos"}), 400

    token = obtener_token()
    payload = {
        "input_data": [{
            "fields": [
                "Animal_ID", "Día", "Alimento_Consumido_kg", "Pasos_por_día",
                "Horas_de_Reposo", "Temperatura_Corp_C", "Nivel_Actividad"
            ],
            "values":
            datos["values"]
        }]
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(DEPLOYMENT_URL, headers=headers, json=payload)
        predicciones = r.json()["predictions"][0]["values"]
        resultados = []
        for i, p in enumerate(predicciones):
            row = datos["values"][i]
            resultados.append({
                "Animal_ID": row[0],
                "Día": row[1],
                "Alimento_Consumido_kg": row[2],
                "Pasos_por_día": row[3],
                "Horas_de_Reposo": row[4],
                "Temperatura_Corp_C": row[5],
                "Nivel_Actividad": row[6],
                "prediction": p[0]
            })
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
