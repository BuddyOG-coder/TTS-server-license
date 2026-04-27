from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

LICENSE_FILE = "licenses.json"

# CHANGE THIS to your own private admin password
ADMIN_KEY = "drexx-admin-92741"


def load_licenses():
    if not os.path.exists(LICENSE_FILE):
        return {}

    with open(LICENSE_FILE, "r") as f:
        return json.load(f)


def save_licenses(data):
    with open(LICENSE_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def home():
    return "Drexx License Server Running"


@app.route("/check-license", methods=["POST"])
def check_license():
    data = request.json or {}

    key = data.get("key", "").strip().upper()
    hwid = data.get("hardware_id", "").strip()

    licenses = load_licenses()

    if key not in licenses:
        return jsonify({"valid": False, "reason": "Key not found"})

    entry = licenses[key]

    if not entry.get("active", False):
        return jsonify({"valid": False, "reason": "Key disabled"})

    if entry.get("hardware_id", "") == "":
        entry["hardware_id"] = hwid
        save_licenses(licenses)

    elif entry.get("hardware_id") != hwid:
        return jsonify({"valid": False, "reason": "Key already used on another PC"})

    return jsonify({
        "valid": True,
        "key": key,
        "hardware_id": entry.get("hardware_id", "")
    })


@app.route("/admin/licenses", methods=["GET"])
def admin_licenses():
    admin_key = request.args.get("admin_key", "")

    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    licenses = load_licenses()
    return jsonify(licenses)


@app.route("/admin/reset-key", methods=["POST"])
def admin_reset_key():
    data = request.json or {}

    admin_key = data.get("admin_key", "")
    key = data.get("key", "").strip().upper()

    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    licenses = load_licenses()

    if key not in licenses:
        return jsonify({"success": False, "reason": "Key not found"})

    licenses[key]["hardware_id"] = ""
    save_licenses(licenses)

    return jsonify({"success": True, "message": f"{key} hardware_id reset"})


@app.route("/admin/disable-key", methods=["POST"])
def admin_disable_key():
    data = request.json or {}

    admin_key = data.get("admin_key", "")
    key = data.get("key", "").strip().upper()

    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    licenses = load_licenses()

    if key not in licenses:
        return jsonify({"success": False, "reason": "Key not found"})

    licenses[key]["active"] = False
    save_licenses(licenses)

    return jsonify({"success": True, "message": f"{key} disabled"})


@app.route("/admin/enable-key", methods=["POST"])
def admin_enable_key():
    data = request.json or {}

    admin_key = data.get("admin_key", "")
    key = data.get("key", "").strip().upper()

    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    licenses = load_licenses()

    if key not in licenses:
        return jsonify({"success": False, "reason": "Key not found"})

    licenses[key]["active"] = True
    save_licenses(licenses)

    return jsonify({"success": True, "message": f"{key} enabled"})


@app.route("/admin/add-key", methods=["POST"])
def admin_add_key():
    data = request.json or {}

    admin_key = data.get("admin_key", "")
    key = data.get("key", "").strip().upper()

    if admin_key != ADMIN_KEY:
        return jsonify({"error": "Unauthorized"}), 403

    if not key:
        return jsonify({"success": False, "reason": "Missing key"})

    licenses = load_licenses()

    if key in licenses:
        return jsonify({"success": False, "reason": "Key already exists"})

    licenses[key] = {
        "active": True,
        "hardware_id": ""
    }

    save_licenses(licenses)

    return jsonify({"success": True, "message": f"{key} added"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
