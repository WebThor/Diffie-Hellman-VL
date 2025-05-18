# Diffie‑Hellman Playground 🎨🔢

**Zwei zusammenhängende Demos – Farben *****und***** Zahlen – zum Verständnis des Diffie‑Hellman‑Schlüssel­austauschs.**
Lernende starten mit einer anschaulichen *Farbmischungs‑Metapher* und wechseln anschließend nahtlos zur formellen *Modulo‑Arithmetik*.

---

## ✨ Funktionen

| Demo                                   | Highlights                         | Route |
| -------------------------------------- | ---------------------------------- | ----- |
| **Farb‑Modus**                         | • Farb‑Picker & HEX‑Eingabe        |       |
| • Schritt‑für‑Schritt‑Mischung         |                                    |       |
| • Sofortiger Farb‑/Schlüssel‑Vergleich | `/colors`                          |       |
| **Zahlen‑Modus**                       | • Prüfung auf Primzahl & Generator |       |
| • Modulare Exponentiation im Backend   |                                    |       |
| • Farb‑Analogie direkt im UI           | `/numeric`                         |       |
| **Startseite**                         | Schnelle Modus‑Auswahl             | `/`   |

---

## 🗺️ Projektstruktur

```text
project/
│ app.py                 # Flask‑Backend (API + Routing)
│ requirements.txt       # Python‑Abhängigkeiten
└──templates/
    ├ index.html         # Startseite
    ├ colors.html        # Farb‑Demo UI
    └ numeric.html       # Zahlen‑Demo UI (mit Farb‑Analogie)
```

---

## 🚀 Schnellstart

```bash
# 1. Repository klonen
$ git clone https://github.com/<dein‑orga>/diffie‑hellman‑playground.git
$ cd diffie‑hellman‑playground

# 2. (Optional) virtuelles Env anlegen
$ python -m venv .venv && source .venv/bin/activate

# 3. Abhängigkeiten installieren
$ pip install -r requirements.txt

# 4. Server starten
$ flask run    # oder: python app.py

# 5. Öffnen
#   http://127.0.0.1:5000/  → Startseite
```

> **Voraussetzungen:** Python ≥ 3.9

---

## 🔌 API‑Endpunkte

| Methode | URL              | Zweck                              | Payload‑Schlüssel                       |
| ------- | ---------------- | ---------------------------------- | --------------------------------------- |
| `POST`  | `/set_base`      | Basisfarbe speichern               | `baseColor`                             |
| `POST`  | `/mix`           | Zwei Farben mischen                | `color1`, `color2`                      |
| `POST`  | `/final`         | End‑Farbschlüssel berechnen        | `baseColor`, `aliceSecret`, `bobSecret` |
| `POST`  | `/set_params`    | Primzahl p & Generator g prüfen    | `prime`, `generator`                    |
| `POST`  | `/public_key`    | Öffentlichen Schlüssel (A/B) holen | `prime`, `generator`, `secret`          |
| `POST`  | `/shared_secret` | Gemeinsamen Schlüssel ableiten     | `prime`, `secret`, `received_public`    |

Alle Endpunkte liefern JSON und geben bei ungültigen Eingaben **Status 400** zurück.

---

## 🧑‍🎓 Didaktische Brücke

| Konzept               | Farb‑Demo                  | Zahlen‑Demo                        |
| --------------------- | -------------------------- | ---------------------------------- |
| Öffentliche Basis     | *Basisfarbe*               | Primzahl **p**, Generator **g**    |
| Geheime Zutat         | Alice/Bob *Geheimfarbe*    | Geheimer Exponent **a / b**        |
| Öffentliche Nachricht | Gemischte Farbe `mix(p,a)` | Öffentlicher Schlüssel `g^a mod p` |
| Gemeinsamer Schlüssel | `mix(p, mix(a,b))`         | `B^a mod p = A^b mod p`            |

---

## 📸 Screenshots

> Hier einfügen: GIF oder Bilder beider Modi in Aktion.

---

## 🤝 Mitwirken

1. Forken
2. Feature‑Branch erstellen (`git checkout -b feat/meine‑idee`)
3. Änderungen committen (`git commit -m 'feat: ...'`)
4. Branch pushen (`git push origin feat/meine‑idee`)
5. Pull‑Request öffnen 🎉

---

## 🪪 Lizenz

MIT © 2025 \Thorsten Weber

Viel Spaß beim Verwenden, Ändern und Teilen! 🙌
