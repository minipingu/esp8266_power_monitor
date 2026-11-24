"""
ESP8266 Multi-Rail Power Supply Monitor Firmware (MicroPython)
Monitors:
- 12V Rail (up to 30A)
- 5V Rail (up to 20A)
- 3.3V Rail (up to 10A)
- Temperature & Humidity (DHT22 / DHT11)
- Built-in Web Server + REST JSON API + Serial Telemetry
"""
import machine
from machine import Pin, I2C
import time
import ujson
import usocket as socket
import dht
import gc
from ads1115 import ADS1115, PGA_6_144V

# Load configuration
try:
    with open("config.json", "r") as f:
        config = ujson.load(f)
except Exception as e:
    print("[ERROR] Cannot read config.json, using defaults:", e)
    config = {}

hw_cfg = config.get("hardware", {})
cal_cfg = config.get("calibration", {})
settings_cfg = config.get("settings", {})

# Initialize I2C Bus
i2c_scl = hw_cfg.get("i2c_scl_pin", 5)  # D1 on NodeMCU
i2c_sda = hw_cfg.get("i2c_sda_pin", 4)  # D2 on NodeMCU
i2c = I2C(scl=Pin(i2c_scl), sda=Pin(i2c_sda), freq=400000)

# Scan I2C
print("[I2C] Scanning bus...")
devices = i2c.scan()
print("[I2C] Detected devices at addresses:", [hex(d) for d in devices])

# Initialize ADC modules
addr1 = hw_cfg.get("adc1_i2c_addr", 0x48)
addr2 = hw_cfg.get("adc2_i2c_addr", 0x49)

adc1 = None
adc2 = None

if addr1 in devices:
    adc1 = ADS1115(i2c, address=addr1, pga=PGA_6_144V)
    print(f"[ADC] ADS1115 #1 initialized at 0x{addr1:02x}")
else:
    print(f"[WARN] ADS1115 #1 not detected at 0x{addr1:02x}")

if addr2 in devices:
    adc2 = ADS1115(i2c, address=addr2, pga=PGA_6_144V)
    print(f"[ADC] ADS1115 #2 initialized at 0x{addr2:02x}")
else:
    print(f"[WARN] ADS1115 #2 not detected at 0x{addr2:02x}")

# Initialize DHT Sensor
dht_pin_num = hw_cfg.get("dht_pin", 14)  # D5 on NodeMCU
dht_type = hw_cfg.get("dht_type", "DHT22").upper()
dht_sensor = None
try:
    if dht_type == "DHT11":
        dht_sensor = dht.DHT11(Pin(dht_pin_num))
    else:
        dht_sensor = dht.DHT22(Pin(dht_pin_num))
    print(f"[DHT] {dht_type} initialized on GPIO{dht_pin_num}")
except Exception as e:
    print("[WARN] DHT initialization error:", e)

# Global Telemetry State
current_telemetry = {
    "rail_12v": {"v": 0.0, "i": 0.0, "p": 0.0, "max_i": 30.0},
    "rail_5v":  {"v": 0.0, "i": 0.0, "p": 0.0, "max_i": 20.0},
    "rail_3v3": {"v": 0.0, "i": 0.0, "p": 0.0, "max_i": 10.0},
    "total_power": 0.0,
    "env": {"temp_c": 0.0, "humidity": 0.0},
    "timestamp_ms": 0,
    "status": "INIT"
}

last_dht_read = 0

def measure_sensors():
    global last_dht_read
    cal_12 = cal_cfg.get("rail_12v", {})
    cal_5  = cal_cfg.get("rail_5v", {})
    cal_33 = cal_cfg.get("rail_3v3", {})

    v12, i12 = 0.0, 0.0
    v5,  i5  = 0.0, 0.0
    v33, i33 = 0.0, 0.0

    # 1. Read ADS1115 #1 (12V & 5V)
    if adc1:
        try:
            # Channel A0: 12V Voltage Divider
            raw_v12 = adc1.read_voltage(0, samples=4)
            v12 = raw_v12 * cal_12.get("v_scale", 5.0) * cal_12.get("v_trim", 1.0)
            if v12 < 0.2:
                v12 = 0.0

            # Channel A1: 12V ACS712-30A Current
            raw_i12 = adc1.read_voltage(1, samples=6)
            zero_12 = cal_12.get("i_zero_volts", 2.500)
            sens_12 = cal_12.get("i_sensitivity", 0.066)
            i12 = (raw_i12 - zero_12) / sens_12
            if abs(i12) < 0.15:  # Noise floor threshold
                i12 = 0.0
            if i12 < 0:
                i12 = 0.0  # Unidirectional assumption for DC load

            # Channel A2: 5V Voltage Divider
            raw_v5 = adc1.read_voltage(2, samples=4)
            v5 = raw_v5 * cal_5.get("v_scale", 5.0) * cal_5.get("v_trim", 1.0)
            if v5 < 0.2:
                v5 = 0.0

            # Channel A3: 5V ACS712-20A Current
            raw_i5 = adc1.read_voltage(3, samples=6)
            zero_5 = cal_5.get("i_zero_volts", 2.500)
            sens_5 = cal_5.get("i_sensitivity", 0.100)
            i5 = (raw_i5 - zero_5) / sens_5
            if abs(i5) < 0.10:
                i5 = 0.0
            if i5 < 0:
                i5 = 0.0
        except Exception as e:
            print("[ADC1 Error]", e)

    # 2. Read ADS1115 #2 (3.3V)
    if adc2:
        try:
            # Channel A0: 3.3V Voltage Divider
            raw_v33 = adc2.read_voltage(0, samples=4)
            v33 = raw_v33 * cal_33.get("v_scale", 5.0) * cal_33.get("v_trim", 1.0)
            if v33 < 0.2:
                v33 = 0.0

            # Channel A1: 3.3V ACS712-20A Current
            raw_i33 = adc2.read_voltage(1, samples=6)
            zero_33 = cal_33.get("i_zero_volts", 2.500)
            sens_33 = cal_33.get("i_sensitivity", 0.100)
            i33 = (raw_i33 - zero_33) / sens_33
            if abs(i33) < 0.08:
                i33 = 0.0
            if i33 < 0:
                i33 = 0.0
        except Exception as e:
            print("[ADC2 Error]", e)

    # 3. Read DHT Sensor (every 2.5 seconds max)
    now = time.ticks_ms()
    if dht_sensor and (time.ticks_diff(now, last_dht_read) > 2500 or last_dht_read == 0):
        try:
            dht_sensor.measure()
            current_telemetry["env"]["temp_c"] = round(dht_sensor.temperature(), 1)
            current_telemetry["env"]["humidity"] = round(dht_sensor.humidity(), 1)
            last_dht_read = now
        except Exception:
            pass

    # Powers
    p12 = v12 * i12
    p5  = v5 * i5
    p33 = v33 * i33
    total_p = p12 + p5 + p33

    # Update state
    current_telemetry["rail_12v"] = {"v": round(v12, 2), "i": round(i12, 2), "p": round(p12, 2), "max_i": 30.0}
    current_telemetry["rail_5v"]  = {"v": round(v5, 2),  "i": round(i5, 2),  "p": round(p5, 2),  "max_i": 20.0}
    current_telemetry["rail_3v3"] = {"v": round(v33, 2), "i": round(i33, 2), "p": round(p33, 2), "max_i": 10.0}
    current_telemetry["total_power"] = round(total_p, 2)
    current_telemetry["timestamp_ms"] = now
    current_telemetry["status"] = "OK"

    return current_telemetry

# HTML Dashboard Page
HTML_PAGE = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ESP8266 Power Supply Monitor</title>
<style>
:root{--bg:#0f172a;--card:#1e293b;--text:#f8fafc;--text-dim:#94a3b8;--border:#334155}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;padding:16px}
header{text-align:center;margin-bottom:20px;padding:10px}
h1{font-size:1.6rem;color:#38bdf8}
.subtitle{color:var(--text-dim);font-size:0.9rem;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;max-width:1200px;margin:0 auto}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px;box-shadow:0 4px 6px rgba(0,0,0,0.3)}
.card-title{font-size:1.15rem;font-weight:700;display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.c-12{border-top:4px solid #eab308}.c-5{border-top:4px solid #ef4444}.c-3{border-top:4px solid #f97316}.c-env{border-top:4px solid #a855f7}.c-tot{border-top:4px solid #10b981}
.val-row{display:flex;justify-content:space-between;margin:10px 0;font-size:1.1rem}
.big-val{font-size:1.8rem;font-weight:700}
.unit{font-size:0.9rem;color:var(--text-dim);font-weight:400}
.bar-bg{background:#334155;border-radius:6px;height:12px;overflow:hidden;margin-top:8px}
.bar-fill{height:100%;transition:width .4s ease}
.fill-12{background:#eab308}.fill-5{background:#ef4444}.fill-3{background:#f97316}
.btn{background:#0284c7;color:#fff;border:none;padding:10px 16px;border-radius:6px;cursor:pointer;font-weight:600;margin-top:14px;width:100%}
.btn:hover{background:#0369a1}
footer{text-align:center;margin-top:24px;color:var(--text-dim);font-size:0.8rem}
</style>
</head>
<body>
<header>
  <h1>ESP8266 Multi-Rail Power Monitor</h1>
  <div class="subtitle">12V/30A | 5V/20A | 3.3V/10A &bull; I2C ADS1115 + ACS712 + DHT22</div>
</header>
<div class="grid">
  <!-- 12V Rail -->
  <div class="card c-12">
    <div class="card-title"><span style="color:#eab308">Rel 12 Volt</span><span class="unit">Max 30A</span></div>
    <div class="val-row"><span>Tegangan:</span><span class="big-val" id="v12">0.00 <span class="unit">V</span></span></div>
    <div class="val-row"><span>Arus Beban:</span><span class="big-val" id="i12">0.00 <span class="unit">A</span></span></div>
    <div class="val-row"><span>Daya Rel:</span><span id="p12" style="font-weight:600">0.00 W</span></div>
    <div class="bar-bg"><div id="b12" class="bar-fill fill-12" style="width:0%"></div></div>
  </div>

  <!-- 5V Rail -->
  <div class="card c-5">
    <div class="card-title"><span style="color:#ef4444">Rel 5 Volt</span><span class="unit">Max 20A</span></div>
    <div class="val-row"><span>Tegangan:</span><span class="big-val" id="v5">0.00 <span class="unit">V</span></span></div>
    <div class="val-row"><span>Arus Beban:</span><span class="big-val" id="i5">0.00 <span class="unit">A</span></span></div>
    <div class="val-row"><span>Daya Rel:</span><span id="p5" style="font-weight:600">0.00 W</span></div>
    <div class="bar-bg"><div id="b5" class="bar-fill fill-5" style="width:0%"></div></div>
  </div>

  <!-- 3.3V Rail -->
  <div class="card c-3">
    <div class="card-title"><span style="color:#f97316">Rel 3.3 Volt</span><span class="unit">Max 10A</span></div>
    <div class="val-row"><span>Tegangan:</span><span class="big-val" id="v33">0.00 <span class="unit">V</span></span></div>
    <div class="val-row"><span>Arus Beban:</span><span class="big-val" id="i33">0.00 <span class="unit">A</span></span></div>
    <div class="val-row"><span>Daya Rel:</span><span id="p33" style="font-weight:600">0.00 W</span></div>
    <div class="bar-bg"><div id="b33" class="bar-fill fill-3" style="width:0%"></div></div>
  </div>

  <!-- Total Summary -->
  <div class="card c-tot">
    <div class="card-title"><span style="color:#10b981">Total Konsumsi Daya</span></div>
    <div style="text-align:center;padding:12px 0">
      <div class="big-val" style="font-size:2.8rem;color:#10b981" id="ptot">0.00 <span class="unit">W</span></div>
    </div>
    <div class="val-row"><span>Status Sistem:</span><span id="status" style="color:#38bdf8;font-weight:600">AKTIF</span></div>
  </div>

  <!-- Temperature & Humidity -->
  <div class="card c-env">
    <div class="card-title"><span style="color:#a855f7">Suhu & Kelembaban</span><span class="unit">DHT22</span></div>
    <div class="val-row"><span>Suhu Ruang/PSU:</span><span class="big-val" id="temp">0.0 <span class="unit">&deg;C</span></span></div>
    <div class="val-row"><span>Kelembaban Udara:</span><span class="big-val" id="hum">0.0 <span class="unit">% RH</span></span></div>
  </div>
</div>
<footer>ESP8266 MicroPython Power Monitor &bull; Update Otomatis Setiap 1 Detik</footer>
<script>
async function updateData(){
  try{
    const res = await fetch('/api/data');
    const d = await res.json();
    document.getElementById('v12').innerHTML = d.rail_12v.v.toFixed(2) + ' <span class="unit">V</span>';
    document.getElementById('i12').innerHTML = d.rail_12v.i.toFixed(2) + ' <span class="unit">A</span>';
    document.getElementById('p12').innerText = d.rail_12v.p.toFixed(2) + ' W';
    document.getElementById('b12').style.width = Math.min((d.rail_12v.i / 30.0)*100, 100) + '%';

    document.getElementById('v5').innerHTML = d.rail_5v.v.toFixed(2) + ' <span class="unit">V</span>';
    document.getElementById('i5').innerHTML = d.rail_5v.i.toFixed(2) + ' <span class="unit">A</span>';
    document.getElementById('p5').innerText = d.rail_5v.p.toFixed(2) + ' W';
    document.getElementById('b5').style.width = Math.min((d.rail_5v.i / 20.0)*100, 100) + '%';

    document.getElementById('v33').innerHTML = d.rail_3v3.v.toFixed(2) + ' <span class="unit">V</span>';
    document.getElementById('i33').innerHTML = d.rail_3v3.i.toFixed(2) + ' <span class="unit">A</span>';
    document.getElementById('p33').innerText = d.rail_3v3.p.toFixed(2) + ' W';
    document.getElementById('b33').style.width = Math.min((d.rail_3v3.i / 10.0)*100, 100) + '%';

    document.getElementById('ptot').innerHTML = d.total_power.toFixed(2) + ' <span class="unit">W</span>';
    document.getElementById('temp').innerHTML = d.env.temp_c.toFixed(1) + ' <span class="unit">&deg;C</span>';
    document.getElementById('hum').innerHTML = d.env.humidity.toFixed(1) + ' <span class="unit">% RH</span>';
  }catch(e){}
}
setInterval(updateData, 1000);
updateData();
</script>
</body>
</html>"""

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 80))
    s.listen(4)
    s.setblocking(False)
    print("[HTTP] Web Server running on port 80...")
    return s

def run():
    server = start_server()
    last_sample_time = 0
    sample_interval = settings_cfg.get("sample_interval_ms", 500)
    serial_json = settings_cfg.get("serial_output_json", True)

    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_sample_time) >= sample_interval:
            last_sample_time = now
            data = measure_sensors()

            # Output telemetry to Serial port for Desktop Monitor or Terminal
            if serial_json:
                print("JSON:" + ujson.dumps(data))
            else:
                print(f"[12V] {data['rail_12v']['v']}V {data['rail_12v']['i']}A | "
                      f"[5V] {data['rail_5v']['v']}V {data['rail_5v']['i']}A | "
                      f"[3.3V] {data['rail_3v3']['v']}V {data['rail_3v3']['i']}A | "
                      f"[P] {data['total_power']}W | [T] {data['env']['temp_c']}C [H] {data['env']['humidity']}%")

        # Handle non-blocking HTTP requests
        try:
            cl, addr = server.accept()
            cl.settimeout(2.0)
            request = cl.recv(1024).decode('utf-8')
            first_line = request.split('\r\n')[0] if request else ""
            
            if "GET /api/data" in first_line:
                body = ujson.dumps(current_telemetry)
                response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nConnection: close\r\n\r\n" + body
                cl.sendall(response.encode('utf-8'))
            else:
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n" + HTML_PAGE
                cl.sendall(response.encode('utf-8'))
            cl.close()
        except OSError:
            pass  # No incoming connection, normal for non-blocking socket
        except Exception as e:
            pass

        time.sleep_ms(10)

if __name__ == "__main__":
    run()
