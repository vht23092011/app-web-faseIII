from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

API_KEY = "OLBXRaXK8m9MrmPa8O_d3QV2nH_oGJ0fBCZ3d-b5dwIZ"
DEPLOYMENT_URL = "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/TU_DEPLOYMENT_ID/predictions?version=2021-05-01"

def get_token():
    r = requests.post("https://iam.cloud.ibm.com/identity/token",
                      data={"apikey": API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"},
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
    return r.json().get("access_token", "")

@app.route("/api/predict", methods=["POST"])
def predict():
    values = request.json["values"]
    token = get_token()
    payload = { "input_data": [{
        "fields": ["Animal_ID", "Día", "Alimento_Consumido_kg", "Pasos_por_día", "Horas_de_Reposo", "Temperatura_Corp_C", "Nivel_Actividad"],
        "values": [[v["Animal_ID"], int(v["Día"]), float(v["Alimento_Consumido_kg"]), int(v["Pasos_por_día"]),
                    float(v["Horas_de_Reposo"]), float(v["Temperatura_Corp_C"]), v["Nivel_Actividad"]] for v in values]
    }]}

    r = requests.post(DEPLOYMENT_URL, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }, json=payload)

    if r.status_code == 200:
        pred = r.json()["predictions"][0]["values"]
        result = []
        for i, val in enumerate(values):
            val["prediction"] = pred[i][0]
            result.append(val)
        return jsonify(result)
    else:
        return jsonify({"error": r.text}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
