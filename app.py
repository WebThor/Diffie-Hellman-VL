from flask import Flask, render_template, request, jsonify
import re
import math

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Hilfsfunktionen für Farben
# ---------------------------------------------------------------------------
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def mix_colors(hex1, hex2):
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    rgb_sorted = sorted([rgb1, rgb2])
    mixed_rgb = tuple((a + b) // 2 for a, b in zip(*rgb_sorted))
    return rgb_to_hex(mixed_rgb)

def mix_three_colors(hex1, hex2, hex3):
    rgb1, rgb2, rgb3 = map(hex_to_rgb, (hex1, hex2, hex3))
    mixed_rgb = tuple((a + b + c) // 3 for a, b, c in zip(rgb1, rgb2, rgb3))
    return rgb_to_hex(mixed_rgb)

def validate_hex(hex_code):
    return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", hex_code))

# ---------------------------------------------------------------------------
# Hilfsfunktionen für Zahlen-Demo
# ---------------------------------------------------------------------------
def is_prime(n: int) -> bool:
    """Einfache, aber für Demo-Zwecke ausreichende Primzahlprüfung."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    r = int(math.isqrt(n)) + 1
    return all(n % i for i in range(3, r, 2))

def validate_int(x: str) -> bool:
    return bool(re.fullmatch(r"\d+", str(x)))

def modexp(base: int, exp: int, mod: int) -> int:
    """Schnelle modulare Exponentiation."""
    return pow(base, exp, mod)

# ---------------------------------------------------------------------------
# Routen – UI-Seiten
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

# ---------------------------------------------------------------------------
# API-Endpunkte – Farben-Demo
# ---------------------------------------------------------------------------
@app.route("/set_base", methods=["POST"])
def set_base():
    data = request.get_json()
    color = data.get("baseColor")
    if not validate_hex(color):
        return jsonify({"error": "Invalid base color"}), 400
    return jsonify({"status": "ok", "confirmedColor": color})

@app.route("/mix", methods=["POST"])
def mix():
    data = request.get_json()
    color1, color2 = data.get("color1"), data.get("color2")

    if not (validate_hex(color1) and validate_hex(color2)):
        return jsonify({"error": "Invalid HEX colors."}), 400

    mixed = mix_colors(color1, color2)
    return jsonify({"mixedColor": mixed, "components": [color1, color2]})

@app.route("/final", methods=["POST"])
def final_mix():
    data = request.get_json()
    base, alice, bob = data.get("baseColor"), data.get("aliceSecret"), data.get("bobSecret")

    if not all(map(validate_hex, [base, alice, bob])):
        return jsonify({"error": "Invalid HEX colors."}), 400

    inner_mix = mix_colors(alice, bob)
    result = mix_colors(base, inner_mix)

    return jsonify({
        "finalColor": result,
        "components": [base, alice, bob],
        "intermediate": inner_mix
    })

# ---------------------------------------------------------------------------
# API-Endpunkte – Zahlen-Demo
# ---------------------------------------------------------------------------
@app.route("/set_params", methods=["POST"])
def set_params():
    data = request.get_json()
    p_raw, g_raw = data.get("prime"), data.get("generator")

    if not (validate_int(p_raw) and validate_int(g_raw)):
        return jsonify({"error": "Ungültige Zahlen."}), 400

    p, g = int(p_raw), int(g_raw)
    if not is_prime(p) or not (1 < g < p):
        return jsonify({"error": "p muss prim sein und 1 < g < p."}), 400

    return jsonify({"status": "ok", "p": p, "g": g})

@app.route("/public_key", methods=["POST"])
def public_key():
    data = request.get_json()
    p, g, secret = map(int, (data["prime"], data["generator"], data["secret"]))
    public_val = modexp(g, secret, p)
    return jsonify({"public": public_val})

@app.route("/shared_secret", methods=["POST"])
def shared_secret():
    data = request.get_json()
    p           = int(data["prime"])
    secret      = int(data["secret"])
    received_pk = int(data["received_public"])
    shared      = modexp(received_pk, secret, p)
    return jsonify({"shared": shared})

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
