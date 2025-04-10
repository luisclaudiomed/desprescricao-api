from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from math import ceil

app = Flask(__name__)

# Equivalência com Diazepam conforme Manual de Ashton
EQUIVALENCIAS_DIAZEPAM = {
    "alprazolam": 20,
    "bromazepam": 5,
    "chlordiazepoxide": 25,
    "clobazam": 20,
    "clonazepam": 20,
    "diazepam": 1,
    "flunitrazepam": 20,
    "lorazepam": 10,
    "lormetazepam": 10,
    "nitrazepam": 10,
    "oxazepam": 15,
    "temazepam": 20,
    "triazolam": 20
}

@app.route('/')
def home():
    return jsonify({"message": "API de desprescrição funcionando"})

@app.route('/desprescrever')
def desprescrever():
    benzo = request.args.get("benzo", "").lower()
    destino = request.args.get("destino", "").lower()
    data_inicio = request.args.get("inicio", "2025-03-27")

    # Validação da dose
    try:
        dose_mg = float(request.args.get("dose", "0"))
    except ValueError:
        return jsonify({"erro": "Dose inválida. Use um número válido em mg."}), 400

    if dose_mg <= 0:
        return jsonify({"erro": "A dose deve ser maior que zero."}), 400

    # Validação de benzo e destino
    if benzo not in EQUIVALENCIAS_DIAZEPAM:
        return jsonify({"erro": f"Benzodiazepínico '{benzo}' inválido."}), 400
    if destino not in ["clonazepam", "bromazepam"]:
        return jsonify({"erro": "Destino deve ser clonazepam ou bromazepam"}), 400

    # Validação da data
    try:
        data = datetime.strptime(data_inicio, "%Y-%m-%d")
    except ValueError:
        return jsonify({"erro": "Data de início inválida. Use o formato AAAA-MM-DD."}), 400

    try:
        eq_diazepam = dose_mg * EQUIVALENCIAS_DIAZEPAM[benzo]

        if destino == "clonazepam":
            dose_mg_destino = eq_diazepam * 0.05  # 10 mg diazepam = 0.5 mg clonazepam
        else:
            dose_mg_destino = eq_diazepam * 0.066  # 15 mg diazepam = 1 mg bromazepam

        gotas = dose_mg_destino / 0.1  # 0.1 mg por gota
        gotas_iniciais = round(gotas)

        if gotas_iniciais > 100:
            return jsonify({"erro": "A dose calculada excede os limites clínicos de segurança."}), 400

        cronograma = []
        dose_atual = gotas_iniciais
        semana = 1

        while dose_atual >= 1 and semana <= 52:
            cronograma.append({
                "semana": semana,
                "inicio": data.strftime("%d/%m/%Y"),
                "fim": (data + timedelta(days=6)).strftime("%d/%m/%Y"),
                "gotas": ceil(dose_atual)
            })

            # Lógica adaptativa de redução
            if dose_atual > 40:
                dose_atual *= 0.90  # Redução de 10%
            elif dose_atual > 20:
                dose_atual *= 0.95  # Redução de 5%
            else:
                dose_atual -= 1  # Redução mínima de 1 gota

            data += timedelta(days=7)
            semana += 1

        # Semana final com 0 gotas
        cronograma.append({
            "semana": semana,
            "inicio": data.strftime("%d/%m/%Y"),
            "fim": (data + timedelta(days=6)).strftime("%d/%m/%Y"),
            "gotas": 0
        })

        return jsonify({
            "dose_inicial_gotas": gotas_iniciais,
            "equivalencia": f"1 mg de {benzo} ≈ {EQUIVALENCIAS_DIAZEPAM[benzo]} mg de diazepam",
            "cronograma": cronograma
        })

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

# Execução local no Replit
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
