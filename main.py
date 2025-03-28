from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

equivalencias_diazepam = {
    "alprazolam": 0.5,
    "bromazepam": 6,
    "clonazepam": 0.5,
    "diazepam": 10,
    "flunitrazepam": 1,
    "lorazepam": 1,
    "nitrazepam": 10,
    "oxazepam": 20,
    "clobazam": 20,
    "estazolam": 1.5,
    "flurazepam": 22.5,
    "midazolam": 11.25,
    "prazepam": 15,
    "temazepam": 20,
    "triazolam": 0.5
    # "cloxazolam": ???  # Aguardando validação clínica
}

gotas_por_mg = {
    "clonazepam": 0.1,
    "bromazepam": 0.25
}

@app.route("/")
def home():
    return jsonify({"message": "API de desprescrição funcionando"})

@app.route("/desprescrever")
def desprescrever():
    benzo = request.args.get("benzo", "").lower()
    dose = float(request.args.get("dose", 0))
    destino = request.args.get("destino", "").lower()
    inicio = request.args.get("inicio", "")

    if benzo not in equivalencias_diazepam or destino not in gotas_por_mg:
        return jsonify({"erro": "benzodiazepínico desconhecido"}), 400

    try:
        data = datetime.strptime(inicio, "%Y-%m-%d")
    except ValueError:
        return jsonify({"erro": "data inválida"}), 400

    eq_diazepam = dose * (10 / equivalencias_diazepam[benzo])
    mg_destino = eq_diazepam * gotas_por_mg[destino]
    gotas_iniciais = round(mg_destino / gotas_por_mg[destino])

    cronograma = []
    gotas = gotas_iniciais
    semana = 1

    while gotas > 0:
        inicio_semana = data.strftime("%d/%m/%Y")
        fim_semana = (data + timedelta(days=6)).strftime("%d/%m/%Y")
        cronograma.append({
            "semana": semana,
            "inicio": inicio_semana,
            "fim": fim_semana,
            "gotas": max(0, round(gotas))
        })
        data += timedelta(days=7)
        semana += 1
        gotas *= 0.96  # Redução de 4% por semana

    return jsonify({
        "dose_inicial_gotas": round(gotas_iniciais),
        "cronograma": cronograma
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
