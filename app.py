from flask import (
    Flask, render_template, request, jsonify,
    send_from_directory
)
from werkzeug.exceptions import HTTPException
import re
import math
import os
import logging

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------
MAX_SAFE_PRIME = 10 ** 6       # Obergrenze für Demo-Parametrisierung

# ---------------------------------------------------------------------------
# Hilfsfunktionen – Farbmischung
# ---------------------------------------------------------------------------
def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % rgb

def mix_colors(a, b):
    r1, g1, b1 = hex_to_rgb(a)
    r2, g2, b2 = hex_to_rgb(b)
    return rgb_to_hex(((r1+r2)//2, (g1+g2)//2, (b1+b2)//2))

def validate_hex(code):
    return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", code))

# ---------------------------------------------------------------------------
# Hilfsfunktionen – Zahlen
# ---------------------------------------------------------------------------
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    root = int(math.isqrt(n)) + 1
    return all(n % i for i in range(3, root, 2))

def validate_int(s: str) -> bool:
    return bool(re.fullmatch(r"\d+", str(s)))

def _require_positive_int(val, name):
    if not validate_int(val) or int(val) <= 0:
        raise ValueError(f"{name} muss eine positive ganze Zahl sein.")
    return int(val)

# ---------------------------------------------------------------------------
# Error-Handler
# ---------------------------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return e                              # 404, 405 … unverändert
    app.logger.error("Unhandled exception", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

# ---------------------------------------------------------------------------
# Favicon (optional)
# ---------------------------------------------------------------------------
@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

# ---------------------------------------------------------------------------
# UI-Routen
# ---------------------------------------------------------------------------
@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/colors")
def colors():
    return render_template("colors.html")

@app.route("/numeric")
def numeric():
    return render_template("numeric.html")

@app.route("/discrete")
def discrete_math():
    return render_template("discrete_math.html")

# ---------------------------------------------------------------------------
# API – Farben
# ---------------------------------------------------------------------------
@app.route("/set_base", methods=["POST"])
def set_base():
    data = request.get_json(force=True)
    color = data.get("baseColor", "")
    if not validate_hex(color):
        return jsonify({"error": "Invalid base color"}), 400
    return jsonify({"status": "ok", "confirmedColor": color})

@app.route("/mix", methods=["POST"])
def mix():
    data = request.get_json(force=True)
    c1, c2 = data.get("color1", ""), data.get("color2", "")
    if not (validate_hex(c1) and validate_hex(c2)):
        return jsonify({"error": "Invalid HEX colors."}), 400
    return jsonify({"mixedColor": mix_colors(c1, c2), "components": [c1, c2]})

@app.route("/final", methods=["POST"])
def final_mix():
    data = request.get_json(force=True)
    base = data.get("baseColor", "")
    alice = data.get("aliceSecret", "")
    bob = data.get("bobSecret", "")
    if not all(map(validate_hex, (base, alice, bob))):
        return jsonify({"error": "Invalid HEX colors."}), 400
    inner = mix_colors(alice, bob)
    return jsonify({
        "finalColor": mix_colors(base, inner),
        "components": [base, alice, bob],
        "intermediate": inner
    })

# ---------------------------------------------------------------------------
# API – Diffie-Hellman (Zahlen-Modus)
# ---------------------------------------------------------------------------
@app.route("/set_params", methods=["POST"])
def set_params():
    data = request.get_json(force=True)
    p = _require_positive_int(data.get("prime"),      "p")
    g = _require_positive_int(data.get("generator"),  "g")
    if p > MAX_SAFE_PRIME:
        return jsonify({"error": "Zahl zu groß."}), 400
    if not is_prime(p) or not (1 < g < p):
        return jsonify({"error": "p muss prim sein und 1 < g < p."}), 400
    return jsonify({"status": "ok", "p": p, "g": g})

@app.route("/public_key", methods=["POST"])
def public_key():
    data = request.get_json(force=True)
    p = _require_positive_int(data.get("prime"),     "p")
    g = _require_positive_int(data.get("generator"), "g")
    s = _require_positive_int(data.get("secret"),    "secret")
    return jsonify({"public": pow(g, s, p)})

@app.route("/shared_secret", methods=["POST"])
def shared_secret():
    data = request.get_json(force=True)
    p = _require_positive_int(data.get("prime"),         "p")
    s = _require_positive_int(data.get("secret"),        "secret")
    pk = _require_positive_int(data.get("received_public"), "received_public")
    return jsonify({"shared": pow(pk, s, p)})

# ---------------------------------------------------------------------------
# API – Diskrete Exponentialfunktion
# ---------------------------------------------------------------------------
@app.route("/api/discrete_exp", methods=["POST"])
def discrete_exponentiation():
    try:
        data = request.get_json(force=True)
        base = _require_positive_int(data.get("base"), "Basis")
        exp  = _require_positive_int(data.get("exp"),  "Exponent")
        mod  = _require_positive_int(data.get("mod"),  "Modul")
        if mod == 1:
            return jsonify({"result": 0})
        return jsonify({"result": pow(base, exp, mod)})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# ---------------------------------------------------------------------------
# API – Diskreter Logarithmus (Brute-Force-Demo)
# ---------------------------------------------------------------------------
@app.route("/api/discrete_log", methods=["POST"])
def discrete_logarithm():
    try:
        data = request.get_json(force=True)
        base = _require_positive_int(data.get("base"),   "Basis")
        res  = _require_positive_int(data.get("result"), "Ergebnis")
        mod  = _require_positive_int(data.get("mod"),    "Modul")
        if mod > 10_000:
            return jsonify({"error": "Bitte ein kleineres p wählen (<10 000) "
                                     "für die Demonstration."}), 400
        for x in range(mod):
            if pow(base, x, mod) == res:
                return jsonify({"log": x})
        return jsonify({"error": "Kein Exponent x gefunden."}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
