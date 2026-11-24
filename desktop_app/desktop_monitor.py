"""
ESP8266 Power Supply Desktop Monitor (Python GUI)
Real-time monitoring for:
- 12V Rail (up to 30A)
- 5V Rail (up to 20A)
- 3.3V Rail (up to 10A)
- Temperature & Humidity (DHT22)
Supports Serial COM Port, Wi-Fi HTTP Polling, and Simulation Demo Mode.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
import csv
from datetime import datetime
import urllib.request
import urllib.error

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class PowerMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ESP8266 Multi-Rail Power Supply Monitor")
        self.geometry("980x750")
        self.minsize(880, 680)
        self.configure(bg="#0f172a")

        # Connection State
        self.running = False
        self.worker_thread = None
        self.serial_inst = None
        self.csv_file = None
        self.csv_writer = None
        self.is_logging = False

        # Data State
        self.data = {
            "rail_12v": {"v": 0.0, "i": 0.0, "p": 0.0, "max_i": 30.0},
            "rail_5v":  {"v": 0.0, "i": 0.0, "p": 0.0, "max_i": 20.0},
            "rail_3v3": {"v": 0.0, "i": 0.0, "p": 0.0, "max_i": 10.0},
            "total_power": 0.0,
            "env": {"temp_c": 0.0, "humidity": 0.0},
            "status": "DISCONNECTED"
        }

        self.setup_styles()
        self.create_widgets()
        self.refresh_com_ports()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".", background="#0f172a", foreground="#f8fafc", font=("Segoe UI", 10))
        style.configure("TLabel", background="#0f172a", foreground="#f8fafc")
        style.configure("Card.TFrame", background="#1e293b", relief="flat")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#38bdf8")
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#94a3b8")

        # Custom progress bars
        style.configure("Yellow.Horizontal.TProgressbar", troughcolor="#334155", background="#eab308")
        style.configure("Red.Horizontal.TProgressbar", troughcolor="#334155", background="#ef4444")
        style.configure("Orange.Horizontal.TProgressbar", troughcolor="#334155", background="#f97316")

    def create_widgets(self):
        # 1. Top Header
        header_frame = tk.Frame(self, bg="#1e293b", padx=20, pady=12, highlightbackground="#334155", highlightthickness=1)
        header_frame.pack(fill="x", padx=16, pady=(16, 8))

        lbl_title = tk.Label(header_frame, text="⚡ ESP8266 MULTI-RAIL POWER MONITOR", font=("Segoe UI", 16, "bold"), bg="#1e293b", fg="#38bdf8")
        lbl_title.pack(side="left")

        lbl_sub = tk.Label(header_frame, text="12V/30A | 5V/20A | 3.3V/10A | Dual ADS1115 + ACS712 + DHT22", font=("Segoe UI", 10), bg="#1e293b", fg="#94a3b8")
        lbl_sub.pack(side="right", pady=4)

        # 2. Control Toolbar
        ctrl_frame = tk.Frame(self, bg="#1e293b", padx=16, pady=10, highlightbackground="#334155", highlightthickness=1)
        ctrl_frame.pack(fill="x", padx=16, pady=8)

        # Mode Selection
        tk.Label(ctrl_frame, text="Koneksi:", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#f8fafc").grid(row=0, column=0, sticky="w", padx=(0, 6))

        self.mode_var = tk.StringVar(value="Serial USB")
        mode_cb = ttk.Combobox(ctrl_frame, textvariable=self.mode_var, values=["Serial USB", "Wi-Fi (HTTP)", "Mode Simulasi (Demo)"], state="readonly", width=18)
        mode_cb.grid(row=0, column=1, padx=4)
        mode_cb.bind("<<ComboboxSelected>>", self.on_mode_change)

        # Port / IP entries
        self.lbl_target = tk.Label(ctrl_frame, text="COM Port:", bg="#1e293b", fg="#cbd5e1")
        self.lbl_target.grid(row=0, column=2, padx=(12, 4))

        self.port_var = tk.StringVar()
        self.port_cb = ttk.Combobox(ctrl_frame, textvariable=self.port_var, width=14)
        self.port_cb.grid(row=0, column=3, padx=4)

        self.btn_refresh = tk.Button(ctrl_frame, text="⟳ Refresh", command=self.refresh_com_ports, bg="#334155", fg="#f8fafc", relief="flat", padx=8)
        self.btn_refresh.grid(row=0, column=4, padx=4)

        # Connect Button
        self.btn_connect = tk.Button(ctrl_frame, text="▶ Sambungkan", command=self.toggle_connection, bg="#0284c7", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=16, pady=4)
        self.btn_connect.grid(row=0, column=5, padx=(16, 8))

        # CSV Logging Button
        self.btn_log = tk.Button(ctrl_frame, text="⏺ Catat CSV", command=self.toggle_csv_logging, bg="#334155", fg="#f8fafc", font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=4)
        self.btn_log.grid(row=0, column=6, padx=8)

        # 3. Main Display Grid (Cards)
        cards_container = tk.Frame(self, bg="#0f172a")
        cards_container.pack(fill="both", expand=True, padx=16, pady=8)

        # Rail 12V Card
        self.card_12v = self.create_rail_card(cards_container, "REL 12 VOLT", "#eab308", 30.0, "Yellow.Horizontal.TProgressbar")
        self.card_12v["frame"].grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        # Rail 5V Card
        self.card_5v = self.create_rail_card(cards_container, "REL 5 VOLT", "#ef4444", 20.0, "Red.Horizontal.TProgressbar")
        self.card_5v["frame"].grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        # Rail 3.3V Card
        self.card_33v = self.create_rail_card(cards_container, "REL 3.3 VOLT", "#f97316", 10.0, "Orange.Horizontal.TProgressbar")
        self.card_33v["frame"].grid(row=0, column=2, sticky="nsew", padx=6, pady=6)

        cards_container.columnconfigure(0, weight=1)
        cards_container.columnconfigure(1, weight=1)
        cards_container.columnconfigure(2, weight=1)

        # 4. Bottom Summary: Total Power & DHT22 Environmental Card
        bottom_container = tk.Frame(self, bg="#0f172a")
        bottom_container.pack(fill="x", padx=16, pady=8)

        # Total Power Box
        total_frame = tk.Frame(bottom_container, bg="#1e293b", padx=18, pady=14, highlightbackground="#10b981", highlightthickness=2)
        total_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(total_frame, text="TOTAL OUTPUT DAYA (POWER)", font=("Segoe UI", 12, "bold"), bg="#1e293b", fg="#10b981").pack(anchor="w")
        self.lbl_total_power = tk.Label(total_frame, text="0.00 W", font=("Segoe UI", 32, "bold"), bg="#1e293b", fg="#10b981")
        self.lbl_total_power.pack(anchor="w", pady=4)
        self.lbl_status = tk.Label(total_frame, text="Status: Siap menghubungkan...", font=("Segoe UI", 9), bg="#1e293b", fg="#94a3b8")
        self.lbl_status.pack(anchor="w")

        # Environment (DHT22) Box
        dht_frame = tk.Frame(bottom_container, bg="#1e293b", padx=18, pady=14, highlightbackground="#a855f7", highlightthickness=2)
        dht_frame.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(dht_frame, text="SENSOR LINGKUNGAN (DHT22)", font=("Segoe UI", 12, "bold"), bg="#1e293b", fg="#a855f7").pack(anchor="w")
        dht_row = tk.Frame(dht_frame, bg="#1e293b")
        dht_row.pack(fill="x", pady=6)

        self.lbl_temp = tk.Label(dht_row, text="Suhu: 0.0 °C", font=("Segoe UI", 20, "bold"), bg="#1e293b", fg="#f8fafc")
        self.lbl_temp.pack(side="left", padx=(0, 20))

        self.lbl_hum = tk.Label(dht_row, text="RH: 0.0 %", font=("Segoe UI", 20, "bold"), bg="#1e293b", fg="#38bdf8")
        self.lbl_hum.pack(side="left")

        # 5. Status bar
        self.status_bar = tk.Label(self, text="Status: Disconnected", bg="#0284c7", fg="#ffffff", font=("Segoe UI", 9), anchor="w", padx=12, pady=4)
        self.status_bar.pack(fill="x", side="bottom")

    def create_rail_card(self, parent, title, accent_color, max_i, pbar_style):
        frame = tk.Frame(parent, bg="#1e293b", padx=18, pady=16, highlightbackground=accent_color, highlightthickness=2)

        # Header
        top = tk.Frame(frame, bg="#1e293b")
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text=title, font=("Segoe UI", 13, "bold"), bg="#1e293b", fg=accent_color).pack(side="left")
        tk.Label(top, text=f"Max {max_i:g}A", font=("Segoe UI", 9), bg="#1e293b", fg="#94a3b8").pack(side="right")

        # Voltage
        v_frame = tk.Frame(frame, bg="#1e293b")
        v_frame.pack(fill="x", pady=4)
        tk.Label(v_frame, text="Tegangan:", font=("Segoe UI", 10), bg="#1e293b", fg="#cbd5e1").pack(side="left")
        lbl_v = tk.Label(v_frame, text="0.00 V", font=("Segoe UI", 18, "bold"), bg="#1e293b", fg="#f8fafc")
        lbl_v.pack(side="right")

        # Current
        i_frame = tk.Frame(frame, bg="#1e293b")
        i_frame.pack(fill="x", pady=4)
        tk.Label(i_frame, text="Arus Beban:", font=("Segoe UI", 10), bg="#1e293b", fg="#cbd5e1").pack(side="left")
        lbl_i = tk.Label(i_frame, text="0.00 A", font=("Segoe UI", 18, "bold"), bg="#1e293b", fg=accent_color)
        lbl_i.pack(side="right")

        # Power
        p_frame = tk.Frame(frame, bg="#1e293b")
        p_frame.pack(fill="x", pady=4)
        tk.Label(p_frame, text="Daya Rel:", font=("Segoe UI", 10), bg="#1e293b", fg="#cbd5e1").pack(side="left")
        lbl_p = tk.Label(p_frame, text="0.00 W", font=("Segoe UI", 12, "bold"), bg="#1e293b", fg="#cbd5e1")
        lbl_p.pack(side="right")

        # Load Bar
        tk.Label(frame, text="Persentase Beban Kapasitas:", font=("Segoe UI", 8), bg="#1e293b", fg="#64748b").pack(anchor="w", pady=(8, 2))
        pbar = ttk.Progressbar(frame, style=pbar_style, maximum=max_i, value=0)
        pbar.pack(fill="x", pady=(0, 6))

        return {
            "frame": frame,
            "lbl_v": lbl_v,
            "lbl_i": lbl_i,
            "lbl_p": lbl_p,
            "pbar": pbar,
            "max_i": max_i
        }

    def on_mode_change(self, event=None):
        mode = self.mode_var.get()
        if mode == "Serial USB":
            self.lbl_target.config(text="COM Port:")
            self.btn_refresh.grid()
            self.refresh_com_ports()
        elif mode == "Wi-Fi (HTTP)":
            self.lbl_target.config(text="ESP8266 IP / URL:")
            self.btn_refresh.grid_remove()
            self.port_cb.config(values=["http://192.168.4.1", "http://192.168.1.100"])
            self.port_var.set("http://192.168.4.1")
        else:  # Simulation Demo Mode
            self.lbl_target.config(text="Mode:")
            self.btn_refresh.grid_remove()
            self.port_cb.config(values=["Demo Internal Simulator"])
            self.port_var.set("Demo Internal Simulator")

    def refresh_com_ports(self):
        if not SERIAL_AVAILABLE:
            self.port_cb.config(values=["pyserial missing"])
            self.port_var.set("pyserial missing")
            return
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if ports:
            self.port_cb.config(values=ports)
            self.port_var.set(ports[0])
        else:
            self.port_cb.config(values=["Tidak ada port COM"])
            self.port_var.set("Tidak ada port COM")

    def toggle_connection(self):
        if self.running:
            self.stop_connection()
        else:
            self.start_connection()

    def start_connection(self):
        mode = self.mode_var.get()
        target = self.port_var.get()

        if mode == "Serial USB":
            if not SERIAL_AVAILABLE:
                messagebox.showerror("Error", "pyserial belum terpasang.")
                return
            if not target or target.startswith("Tidak ada"):
                messagebox.showwarning("Peringatan", "Pilih Port COM ESP8266 terlebih dahulu.")
                return
            try:
                self.serial_inst = serial.Serial(target, baudrate=115200, timeout=1.0)
            except Exception as e:
                messagebox.showerror("Gagal Membuka Port", f"Tidak dapat membuka {target}:\n{e}")
                return

        self.running = True
        self.btn_connect.config(text="⏹ Putuskan", bg="#dc2626")
        self.status_bar.config(text=f"Terhubung ke {target} ({mode})", bg="#16a34a")

        self.worker_thread = threading.Thread(target=self.worker_loop, daemon=True)
        self.worker_thread.start()

    def stop_connection(self):
        self.running = False
        if self.serial_inst and self.serial_inst.is_open:
            try:
                self.serial_inst.close()
            except Exception:
                pass
            self.serial_inst = None

        self.btn_connect.config(text="▶ Sambungkan", bg="#0284c7")
        self.status_bar.config(text="Status: Terputus", bg="#0284c7")
        self.lbl_status.config(text="Status: Sambungan dihentikan.")

    def worker_loop(self):
        mode = self.mode_var.get()
        sim_tick = 0

        while self.running:
            try:
                if mode == "Mode Simulasi (Demo)":
                    time.sleep(0.5)
                    sim_tick += 0.2
                    import math
                    v12 = 12.02 + 0.15 * math.sin(sim_tick * 0.5)
                    i12 = 15.0 + 12.0 * math.sin(sim_tick * 0.3)
                    v5  = 5.01 + 0.05 * math.cos(sim_tick * 0.4)
                    i5  = 8.0 + 6.0 * math.cos(sim_tick * 0.6)
                    v33 = 3.30 + 0.03 * math.sin(sim_tick * 0.7)
                    i33 = 4.0 + 3.0 * math.sin(sim_tick * 0.8)
                    temp = 32.5 + 2.0 * math.sin(sim_tick * 0.1)
                    hum = 60.0 + 5.0 * math.cos(sim_tick * 0.1)

                    data = {
                        "rail_12v": {"v": round(v12, 2), "i": round(abs(i12), 2), "p": round(v12 * abs(i12), 2), "max_i": 30.0},
                        "rail_5v":  {"v": round(v5, 2),  "i": round(abs(i5), 2),  "p": round(v5 * abs(i5), 2),  "max_i": 20.0},
                        "rail_3v3": {"v": round(v33, 2), "i": round(abs(i33), 2), "p": round(v33 * abs(i33), 2), "max_i": 10.0},
                        "total_power": round(v12*abs(i12) + v5*abs(i5) + v33*abs(i33), 2),
                        "env": {"temp_c": round(temp, 1), "humidity": round(hum, 1)},
                        "status": "SIMULASI"
                    }
                    self.after(0, self.update_ui, data)

                elif mode == "Wi-Fi (HTTP)":
                    url = self.port_var.get().strip().rstrip("/") + "/api/data"
                    try:
                        req = urllib.request.Request(url, headers={'User-Agent': 'PowerMonitorDesktop'})
                        with urllib.request.urlopen(req, timeout=1.5) as resp:
                            body = resp.read().decode('utf-8')
                            data = json.loads(body)
                            self.after(0, self.update_ui, data)
                    except Exception as e:
                        self.after(0, self.set_status_error, f"HTTP Error: {e}")
                    time.sleep(1.0)

                elif mode == "Serial USB":
                    if self.serial_inst and self.serial_inst.is_open:
                        line = self.serial_inst.readline().decode('utf-8', errors='ignore').strip()
                        if line.startswith("JSON:"):
                            json_str = line[5:]
                            data = json.loads(json_str)
                            self.after(0, self.update_ui, data)
            except Exception as e:
                time.sleep(0.5)

    def set_status_error(self, msg):
        self.lbl_status.config(text=str(msg)[:60], fg="#ef4444")

    def update_ui(self, data):
        self.data = data

        r12 = data.get("rail_12v", {})
        self.card_12v["lbl_v"].config(text=f"{r12.get('v', 0):.2f} V")
        self.card_12v["lbl_i"].config(text=f"{r12.get('i', 0):.2f} A")
        self.card_12v["lbl_p"].config(text=f"{r12.get('p', 0):.2f} W")
        self.card_12v["pbar"]["value"] = min(r12.get('i', 0), 30.0)

        r5 = data.get("rail_5v", {})
        self.card_5v["lbl_v"].config(text=f"{r5.get('v', 0):.2f} V")
        self.card_5v["lbl_i"].config(text=f"{r5.get('i', 0):.2f} A")
        self.card_5v["lbl_p"].config(text=f"{r5.get('p', 0):.2f} W")
        self.card_5v["pbar"]["value"] = min(r5.get('i', 0), 20.0)

        r33 = data.get("rail_3v3", {})
        self.card_33v["lbl_v"].config(text=f"{r33.get('v', 0):.2f} V")
        self.card_33v["lbl_i"].config(text=f"{r33.get('i', 0):.2f} A")
        self.card_33v["lbl_p"].config(text=f"{r33.get('p', 0):.2f} W")
        self.card_33v["pbar"]["value"] = min(r33.get('i', 0), 10.0)

        tot_p = data.get("total_power", 0.0)
        self.lbl_total_power.config(text=f"{tot_p:.2f} W")

        env = data.get("env", {})
        self.lbl_temp.config(text=f"Suhu: {env.get('temp_c', 0):.1f} °C")
        self.lbl_hum.config(text=f"RH: {env.get('humidity', 0):.1f} %")
        self.lbl_status.config(text="Status Telemetri: Normal (Sinkron)", fg="#38bdf8")

        # Log to CSV if active
        if self.is_logging and self.csv_writer:
            try:
                row = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    r12.get('v', 0), r12.get('i', 0), r12.get('p', 0),
                    r5.get('v', 0),  r5.get('i', 0),  r5.get('p', 0),
                    r33.get('v', 0), r33.get('i', 0), r33.get('p', 0),
                    tot_p,
                    env.get('temp_c', 0), env.get('humidity', 0)
                ]
                self.csv_writer.writerow(row)
                self.csv_file.flush()
            except Exception:
                pass

    def toggle_csv_logging(self):
        if self.is_logging:
            self.is_logging = False
            if self.csv_file:
                self.csv_file.close()
                self.csv_file = None
            self.btn_log.config(text="⏺ Catat CSV", bg="#334155")
            messagebox.showinfo("Logging Berhenti", "File log CSV berhasil disimpan.")
        else:
            filename = filedialog.asksaveasfilename(
                title="Pilih Lokasi Simpan Log CSV",
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                initialfile=f"power_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            if filename:
                try:
                    self.csv_file = open(filename, mode="w", newline="", encoding="utf-8")
                    self.csv_writer = csv.writer(self.csv_file)
                    headers = [
                        "Timestamp",
                        "V_12V", "I_12V", "P_12V",
                        "V_5V", "I_5V", "P_5V",
                        "V_3V3", "I_3V3", "P_3V3",
                        "Total_Power_Watts",
                        "Temp_C", "Humidity_Pct"
                    ]
                    self.csv_writer.writerow(headers)
                    self.is_logging = True
                    self.btn_log.config(text="⏹ Hentikan CSV", bg="#dc2626")
                except Exception as e:
                    messagebox.showerror("Gagal Membuka File", str(e))

    def on_close(self):
        self.stop_connection()
        if self.csv_file:
            try:
                self.csv_file.close()
            except Exception:
                pass
        self.destroy()


if __name__ == "__main__":
    app = PowerMonitorApp()
    app.mainloop()
