from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO, emit
import time
import random

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-me"
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def dashboard():
    # Put your stream URLs here (or keep as defaults and override in JS)
    return render_template(
        "dashboard.html",
        stream1_url="/stream/1",
        stream2_url="/stream/2",
    )

# --- Example MJPEG stream endpoints (PLACEHOLDERS) ---
# Replace these with your actual camera streaming code.
@app.route("/stream/<int:cam_id>")
def stream(cam_id: int):
    # This placeholder does not provide real video.
    # Use your existing MJPEG generator or a WebRTC player.
    return Response(
        status=204
    )

# --- Commands endpoint (optional REST) ---
@app.route("/api/command", methods=["POST"])
def api_command():
    payload = request.get_json(force=True)
    cmd = payload.get("command", "")
    # TODO: send cmd to rover (ROS topic / serial / socket etc.)
    print("COMMAND:", cmd)
    return jsonify({"ok": True, "echo": cmd})

# --- Socket.IO handlers ---
@socketio.on("connect")
def on_connect():
    emit("log", {"level": "info", "msg": "UI connected"})
    emit("warning", {"active": False, "msg": ""})

@socketio.on("command")
def on_command(data):
    cmd = (data or {}).get("command", "")
    # TODO: send cmd to rover
    emit("log", {"level": "info", "msg": f"Command sent: {cmd}"})

def telemetry_loop():
    """
    Demo telemetry publisher.
    Replace this with real rover telemetry ingestion.
    """
    t0 = time.time()
    while True:
        # Fake data
        speed = max(0.0, 1.5 + 0.7 * random.random())
        cpu = 20 + 50 * random.random()
        batt = 40 + 60 * random.random()
        wifi = -30 - 40 * random.random()     # dBm-ish
        accel = -0.2 + 0.4 * random.random()  # m/s^2

        now = time.time() - t0
        socketio.emit("telemetry", {
            "ts": now,
            "speed_mps": speed,
            "cpu_pct": cpu,
            "battery_pct": batt,
            "wifi_dbm": wifi,
            "accel_mps2": accel,
            "mode": "TELEOP",
            "armed": True
        })

        # Fake warning example
        if batt < 45:
            socketio.emit("warning", {"active": True, "msg": "Battery low"})
        else:
            socketio.emit("warning", {"active": False, "msg": ""})

        time.sleep(0.25)

if __name__ == "__main__":
    # Start background telemetry demo
    socketio.start_background_task(telemetry_loop)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
