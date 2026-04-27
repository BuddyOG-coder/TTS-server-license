from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

LICENSE_FILE = "licenses.json"

def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return {}
    with open(LICENSE_FILE, "r") as f:
        return json.load(f)

def save_licenses(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/check-license", methods=["POST"])
def check_license():
    data = request.json
    key = data.get("key")
    hwid = data.get("hardware_id")

    licenses = load_licenses()

    if key not in licenses:
        return jsonify({"valid": False, "reason": "Key not found"})

    entry = licenses[key]

    if not entry.get("active", False):
        return jsonify({"valid": False, "reason": "Key disabled"})

    # Lock to first PC
    if entry["hardware_id"] == "":
        entry["hardware_id"] = hwid
        save_licenses(licenses)

    elif entry["hardware_id"] != hwid:
        return jsonify({"valid": False, "reason": "Key already used on another PC"})

    return jsonify({"valid": True})

@app.route("/")
def home():
    return "Drexx License Server Running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)