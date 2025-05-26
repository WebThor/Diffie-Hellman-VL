from flask import Flask, render_template, request, jsonify
import re
import math
import logging

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Logging Setup (useful in production)
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAX_SAFE_PRIME = 10**6

# ---------------------------------------------------------------------------
# Utility Functions – Colors
# ---------------------------------------------------------------------------
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_tuple):
    return '#%02x%02x%02x' % rgb_tuple

def mix_colors(hex1, hex2):
    try:
        rgb1 = hex_to_rgb(hex1)
        rgb2 = hex_to_rgb(hex2)
        mixed_rgb = tuple((a + b) // 2 for a, b in zip(rgb1, rgb2))
        return rgb_to_hex(mixed_rgb)
    except Exception:
        raise ValueError("Color mixing failed.")

def mix_three_colors(hex1, hex2, hex3):
    try:
        rgb1, rgb2, rgb3 = map(hex_to_rgb, (hex1, hex2, hex3))
        mixed_rgb = tuple((a + b + c) // 3 for a, b, c in zip(rgb1, rgb2, rgb3))
        return rgb_to_hex(mixed_rgb)
    except Exception:
        raise ValueError("Color mixing failed.")

def validate_hex(hex_code):
    return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", hex_code))

# ---------------------------------------------------------------------------
# Utility Functions – Numeric
# ---------------------------------------------------------------------------
def is_prime(n: int) -> bool:
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
    return pow(base, exp, mod)

# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({"error": "Internal server error"}), 500

# ---------------------------------------------------------------------------
# UI Routes
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
# API – Colors
# ---------------------------------------------------------------------------
@app.route("/set_base", methods=["POST"])
def set_base():
    try:
        data = request.get_json()
        color = data.get("baseColor", "")
        if not validate_hex(color):
            return jsonify({"error": "Invalid base color"}), 400
        return jsonify({"status": "ok", "confirmedColor": color})
    except Exception as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400

@app.route("/mix", methods=["POST"])
def mix():
    try:
        data = request.get_json()
        color1 = data.get("color1", "")
        color2 = data.get("color2", "")

        if not (validate_hex(color1) and validate_hex(color2)):
            return jsonify({"error": "Invalid HEX colors."}), 400

        mixed = mix_colors(color1, color2)
        return jsonify({"mixedColor": mixed, "components": [color1, color2]})
    except Exception as e:
        return jsonify({"error": f"Mixing failed: {e}"}), 400

@app.route("/final", methods=["POST"])
def final_mix():
    try:
        data = request.get_json()
        base = data.get("baseColor", "")
        alice = data.get("aliceSecret", "")
        bob = data.get("bobSecret", "")

        if not all(map(validate_hex, [base, alice, bob])):
            return jsonify({"error": "Invalid HEX colors."}), 400

        inner_mix = mix_colors(alice, bob)
        result = mix_colors(base, inner_mix)

        return jsonify({
            "finalColor": result,
            "components": [base, alice, bob],
            "intermediate": inner_mix
        })
    except Exception as e:
        return jsonify({"error": f"Mixing failed: {e}"}), 400

# ---------------------------------------------------------------------------
# API – Numeric
# ---------------------------------------------------------------------------
@app.route("/set_params", methods=["POST"])
def set_params():
    try:
        data = request.get_json()
        p_raw, g_raw = data.get("prime"), data.get("generator")

        if not (validate_int(p_raw) and validate_int(g_raw)):
            return jsonify({"error": "Ungültige Zahlen."}), 400

        p, g = int(p_raw), int(g_raw)
        if p > MAX_SAFE_PRIME:
            return jsonify({"error": "Zahl zu groß."}), 400
        if not is_prime(p) or not (1 < g < p):
            return jsonify({"error": "p muss prim sein und 1 < g < p."}), 400

        return jsonify({"status": "ok", "p": p, "g": g})
    except Exception as e:
        return jsonify({"error": f"Fehlerhafte Eingabe: {e}"}), 400

@app.route("/public_key", methods=["POST"])
def public_key():
    try:
        data = request.get_json()
        p = int(data.get("prime"))
        g = int(data.get("generator"))
        secret = int(data.get("secret"))
        public_val = modexp(g, secret, p)
        return jsonify({"public": public_val})
    except (TypeError, ValueError, KeyError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400

@app.route("/shared_secret", methods=["POST"])
def shared_secret():
    try:
        data = request.get_json()
        p = int(data.get("prime"))
        secret = int(data.get("secret"))
        received_pk = int(data.get("received_public"))
        shared = modexp(received_pk, secret, p)
        return jsonify({"shared": shared})
    except (TypeError, ValueError, KeyError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400

# ---------------------------------------------------------------------------
# Main Entry
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import os
    debug_mode = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
