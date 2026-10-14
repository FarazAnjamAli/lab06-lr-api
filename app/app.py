"""
Lab-06 - Linear Regression prediction service (REST API)

    y = a1*x1 + a2*x2 + a3*x3 + b

Coefficients are generated deterministically from the student roll number seed.
"""
import random

from flask import Flask, jsonify, request

# ---------------------------------------------------------------
# >>> EDIT THESE TWO VALUES BEFORE BUILDING THE IMAGE <<<
REGISTRATION_NUMBER = "FA23-BDS-049"   # Faraz Ali
STUDENT_ROLL_NUMBER = 49               # numeric part of FA23-BDS-049
# ---------------------------------------------------------------

# Fixed procedure from the lab handout - do not change the order of calls
seed = STUDENT_ROLL_NUMBER
random.seed(seed)
a1 = random.uniform(-5, 5)
a2 = random.uniform(-5, 5)
a3 = random.uniform(-5, 5)
b = random.uniform(-10, 10)

app = Flask(__name__)
app.json.sort_keys = False  # keep response keys in the order we write them


@app.route("/")
def home():
    return jsonify({
        "service": "Linear Regression Prediction API",
        "usage": "/predict?x1=2&x2=3&x3=1",
    })


@app.route("/health")
def health():
    return jsonify({"status": "UP"})


@app.route("/predict", methods=["GET", "POST"])
def predict():
    # Accept query params (GET) or JSON body / form (POST)
    data = dict(request.args)
    if request.method == "POST":
        data.update(request.get_json(silent=True) or request.form.to_dict())

    try:
        x1 = float(data["x1"])
        x2 = float(data["x2"])
        x3 = float(data["x3"])
    except KeyError as e:
        return jsonify({"error": f"missing parameter {e.args[0]}"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "x1, x2 and x3 must be numbers"}), 400

    y = a1 * x1 + a2 * x2 + a3 * x3 + b

    return jsonify({
        "registration number": REGISTRATION_NUMBER,
        "prediction": round(y, 2),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
