"""
Script to generate ultra-clear, high-resolution wiring diagram PNG
for ESP8266 Multi-Rail Power Supply Monitor.
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 2600, 1800
img = Image.new("RGB", (W, H), color="#0f172a") # Slate-900 dark theme
draw = ImageDraw.Draw(img)

# Try loading standard Windows fonts, fallback to default if not found
try:
    font_title = ImageFont.truetype("arialbd.ttf", 46)
    font_sub = ImageFont.truetype("arial.ttf", 26)
    font_sec = ImageFont.truetype("arialbd.ttf", 30)
    font_box_title = ImageFont.truetype("arialbd.ttf", 26)
    font_bold = ImageFont.truetype("arialbd.ttf", 22)
    font_norm = ImageFont.truetype("arial.ttf", 20)
    font_small = ImageFont.truetype("arial.ttf", 17)
    font_mono = ImageFont.truetype("consola.ttf", 20)
except Exception:
    font_title = font_sub = font_sec = font_box_title = font_bold = font_norm = font_small = font_mono = ImageFont.load_default()

# ----------------- HEADER -----------------
draw.rounded_rectangle([40, 30, W - 40, 130], radius=16, fill="#1e293b", outline="#334155", width=3)
draw.text((70, 48), "DIAGRAM SKEMATIK WIRING: ESP8266 MULTI-RAIL POWER MONITOR", fill="#38bdf8", font=font_title)
draw.text((70, 100), "Rel 12V/30A | Rel 5V/20A | Rel 3.3V/10A | Dual ADS1115 (16-Bit) + ACS712 + Sensor Suhu/Kelembaban DHT22", fill="#94a3b8", font=font_sub)

# ----------------- COLOR LEGEND -----------------
legend_items = [
    ("#eab308", "Jalur 12V (Kabel 10-12 AWG)"),
    ("#ef4444", "Jalur 5V / VCC (Kabel 12-14 AWG)"),
    ("#f97316", "Jalur 3.3V (Kabel 16-18 AWG)"),
    ("#64748b", "Common Ground (GND Bersama)"),
    ("#06b6d4", "Bus I2C (SCL: D1, SDA: D2)"),
    ("#22c55e", "Sinyal Analog ke ADC"),
    ("#a855f7", "Data Digital DHT22 (Pin D5)")
]
draw.rounded_rectangle([40, 145, W - 40, 205], radius=10, fill="#1e293b", outline="#334155", width=2)
lx = 60
for color, label in legend_items:
    draw.ellipse([lx, 165, lx + 20, 185], fill=color)
    draw.text((lx + 28, 163), label, fill="#cbd5e1", font=font_norm)
    lx += 360

# ----------------- HELPER FUNCTIONS -----------------
def draw_card(box, title, header_color="#334155", border_color="#475569", bg="#1e293b"):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=12, fill=bg, outline=border_color, width=2)
    draw.rounded_rectangle([x0, y0, x1, y0 + 44], radius=12, fill=header_color)
    draw.rectangle([x0, y0 + 20, x1, y0 + 44], fill=header_color)
    draw.text((x0 + 16, y0 + 10), title, fill="#ffffff", font=font_box_title)

def draw_pin(x, y, label, color="#cbd5e1", font=font_norm, radius=6):
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
    draw.text((x + 14, y - 11), label, fill=color, font=font)

# ----------------- MODULE 1: POWER SUPPLY (ATX / PSU) -----------------
psu_box = [50, 240, 420, 880]
draw_card(psu_box, "POWER SUPPLY UNIT (PSU)", header_color="#b45309", border_color="#eab308")
draw.text((70, 300), "INPUT DAYA DARI PSU", fill="#fbbf24", font=font_bold)

# Rails inside PSU
rails = [
    ("+12V Output (Kuning)", "Maksimal 30 Ampere", "#eab308", 350),
    ("+5V Output (Merah)", "Maksimal 20 Ampere", "#ef4444", 470),
    ("+3.3V Output (Oranye)", "Maksimal 10 Ampere", "#f97316", 590),
    ("Common GND (Hitam)", "Titik Bintang Ground (Star-GND)", "#94a3b8", 710)
]
for title, sub, col, y in rails:
    draw.rounded_rectangle([70, y, 400, y + 80], radius=8, fill="#0f172a", outline=col, width=2)
    draw.text((85, y + 12), title, fill=col, font=font_bold)
    draw.text((85, y + 44), sub, fill="#94a3b8", font=font_small)

# ----------------- MODULE 2: ACS712 CURRENT SENSORS -----------------
# 12V 30A Sensor
acs12_box = [520, 240, 960, 430]
draw_card(acs12_box, "ACS712 - 30A (Rel 12V)", header_color="#854d0e", border_color="#eab308")
draw.text((540, 295), "Terminal Screw Blok:", fill="#ffffff", font=font_bold)
draw.text((540, 325), "IP+ : Masuk dari +12V PSU (Kabel 10 AWG)", fill="#eab308", font=font_norm)
draw.text((540, 350), "IP- : Keluar ke Beban/Load 12V", fill="#eab308", font=font_norm)
draw.text((540, 385), "Header: VCC=5V | GND=GND | OUT -> ADC1 (0x48) A1", fill="#22c55e", font=font_bold)

# 5V 20A Sensor
acs5_box = [520, 460, 960, 650]
draw_card(acs5_box, "ACS712 - 20A (Rel 5V)", header_color="#991b1b", border_color="#ef4444")
draw.text((540, 515), "Terminal Screw Blok:", fill="#ffffff", font=font_bold)
draw.text((540, 545), "IP+ : Masuk dari +5V PSU (Kabel 12 AWG)", fill="#ef4444", font=font_norm)
draw.text((540, 570), "IP- : Keluar ke Beban/Load 5V", fill="#ef4444", font=font_norm)
draw.text((540, 605), "Header: VCC=5V | GND=GND | OUT -> ADC1 (0x48) A3", fill="#22c55e", font=font_bold)

# 3.3V 10A Sensor (ACS712-20A digunakan untuk max 10A aman)
acs3_box = [520, 680, 960, 870]
draw_card(acs3_box, "ACS712 - 20A (Rel 3.3V, Beban 10A)", header_color="#9a3412", border_color="#f97316")
draw.text((540, 735), "Terminal Screw Blok:", fill="#ffffff", font=font_bold)
draw.text((540, 765), "IP+ : Masuk dari +3.3V PSU (Kabel 16 AWG)", fill="#f97316", font=font_norm)
draw.text((540, 790), "IP- : Keluar ke Beban/Load 3.3V", fill="#f97316", font=font_norm)
draw.text((540, 825), "Header: VCC=5V | GND=GND | OUT -> ADC2 (0x49) A1", fill="#22c55e", font=font_bold)

# ----------------- MODULE 3: VOLTAGE DIVIDERS (0-25V) -----------------
volt_box = [520, 900, 960, 1160]
draw_card(volt_box, "3x SENSOR TEGANGAN (Divider 5:1)", header_color="#0369a1", border_color="#38bdf8")
draw.text((540, 955), "Tipe: Modul Resistor 30k / 7.5k (Rasio 5 banding 1):", fill="#cbd5e1", font=font_norm)
draw.text((540, 990), "• Sensor 12V: VCC dari 12V Rail -> Signal S -> ADC1 A0 (2.4V maks)", fill="#eab308", font=font_norm)
draw.text((540, 1025), "• Sensor 5V : VCC dari 5V Rail  -> Signal S -> ADC1 A2 (1.0V maks)", fill="#ef4444", font=font_norm)
draw.text((540, 1060), "• Sensor 3.3V: VCC dari 3.3V    -> Signal S -> ADC2 A0 (0.66V maks)", fill="#f97316", font=font_norm)
draw.text((540, 1105), "GND Semua Sensor Tegangan -> Hubungkan ke Common Ground", fill="#94a3b8", font=font_bold)

# ----------------- MODULE 4: DUAL ADS1115 (16-BIT ADC) -----------------
# ADC 1 (0x48)
adc1_box = [1030, 240, 1500, 560]
draw_card(adc1_box, "ADS1115 #1 (Alamat I2C: 0x48)", header_color="#0e7490", border_color="#06b6d4")
draw.text((1050, 295), "Konfigurasi Pin Daya & I2C:", fill="#ffffff", font=font_bold)
draw.text((1050, 325), "VDD  -> 5V Rail / NodeMCU VIN", fill="#ef4444", font=font_mono)
draw.text((1050, 350), "GND  -> Common Ground", fill="#cbd5e1", font=font_mono)
draw.text((1050, 375), "SCL  -> NodeMCU Pin D1 (GPIO5)", fill="#06b6d4", font=font_mono)
draw.text((1050, 400), "SDA  -> NodeMCU Pin D2 (GPIO4)", fill="#06b6d4", font=font_mono)
draw.text((1050, 425), "ADDR -> GND (Mengatur Alamat 0x48)", fill="#a855f7", font=font_mono)
draw.line([1045, 455, 1485, 455], fill="#334155", width=2)
draw.text((1050, 465), "Channel Input Analog:", fill="#ffffff", font=font_bold)
draw.text((1050, 495), "A0: Tegangan Rel 12V (Sensor Tegangan)", fill="#22c55e", font=font_norm)
draw.text((1050, 520), "A1: Arus Rel 12V (ACS712-30A OUT)", fill="#22c55e", font=font_norm)
draw.text((1050, 545), "A2: Tegangan Rel 5V (Sensor Tegangan)", fill="#22c55e", font=font_norm)
draw.text((1050, 570), "A3: Arus Rel 5V (ACS712-20A OUT)", fill="#22c55e", font=font_norm)
adc1_box[3] = 610 # adjust height

# ADC 2 (0x49)
adc2_box = [1030, 640, 1500, 970]
draw_card(adc2_box, "ADS1115 #2 (Alamat I2C: 0x49)", header_color="#0e7490", border_color="#06b6d4")
draw.text((1050, 695), "Konfigurasi Pin Daya & I2C:", fill="#ffffff", font=font_bold)
draw.text((1050, 725), "VDD  -> 5V Rail / NodeMCU VIN", fill="#ef4444", font=font_mono)
draw.text((1050, 750), "GND  -> Common Ground", fill="#cbd5e1", font=font_mono)
draw.text((1050, 775), "SCL  -> NodeMCU Pin D1 (GPIO5 Paralel)", fill="#06b6d4", font=font_mono)
draw.text((1050, 800), "SDA  -> NodeMCU Pin D2 (GPIO4 Paralel)", fill="#06b6d4", font=font_mono)
draw.text((1050, 825), "ADDR -> VDD (5V) (Mengatur Alamat 0x49)", fill="#a855f7", font=font_mono)
draw.line([1045, 855, 1485, 855], fill="#334155", width=2)
draw.text((1050, 865), "Channel Input Analog:", fill="#ffffff", font=font_bold)
draw.text((1050, 895), "A0: Tegangan Rel 3.3V (Sensor Tegangan)", fill="#22c55e", font=font_norm)
draw.text((1050, 920), "A1: Arus Rel 3.3V (ACS712-20A OUT)", fill="#22c55e", font=font_norm)
draw.text((1050, 945), "A2 & A3: Cadangan / Spare Input", fill="#64748b", font=font_norm)

# ----------------- MODULE 5: ESP8266 NODEMCU -----------------
esp_box = [1570, 240, 2060, 970]
draw_card(esp_box, "ESP8266 NODEMCU (V3 / ESP-12E)", header_color="#1d4ed8", border_color="#3b82f6")

# Wi-Fi graphic icon
draw.rounded_rectangle([1730, 295, 1890, 350], radius=8, fill="#0f172a", outline="#38bdf8", width=2)
draw.text((1750, 310), "Wi-Fi 2.4GHz", fill="#38bdf8", font=font_bold)

# NodeMCU Pinout list
draw.text((1600, 370), "PIN MIKROKONTROLER DIGUNAKAN:", fill="#ffffff", font=font_bold)
pins = [
    ("VIN", "Input Daya 5V DC (dari Rel 5V PSU / USB)", "#ef4444"),
    ("GND", "Ground Bersama (Common Ground)", "#cbd5e1"),
    ("3V3", "Output 3.3V Regulator internal (ke DHT22 VCC)", "#f97316"),
    ("D1 (GPIO5)", "I2C SCL -> Menuju SCL kedua ADS1115", "#06b6d4"),
    ("D2 (GPIO4)", "I2C SDA -> Menuju SDA kedua ADS1115", "#06b6d4"),
    ("D5 (GPIO14)", "Digital Data -> Menuju Data Pin DHT22", "#a855f7"),
    ("TX/RX", "Serial USB Debug & Komunikasi ke Desktop (115200 bps)", "#fbbf24")
]
py = 410
for p_name, p_desc, p_col in pins:
    draw.rounded_rectangle([1595, py, 2035, py + 52], radius=6, fill="#0f172a", outline="#334155")
    draw.text((1610, py + 12), p_name, fill=p_col, font=font_bold)
    draw.text((1730, py + 14), p_desc, fill="#cbd5e1", font=font_small)
    py += 62

draw.text((1600, 870), "Web Server: http://<ip_esp8266>/", fill="#38bdf8", font=font_bold)
draw.text((1600, 905), "JSON API   : http://<ip_esp8266>/api/data", fill="#38bdf8", font=font_bold)
draw.text((1600, 935), "Serial CLI : 115200 baud, 8N1", fill="#94a3b8", font=font_norm)

# ----------------- MODULE 6: DHT22 SENSOR -----------------
dht_box = [2120, 240, 2550, 560]
draw_card(dht_box, "DHT22 (AM2302) SENSOR", header_color="#7e22ce", border_color="#a855f7")
draw.text((2140, 295), "Sensor Suhu & Kelembaban:", fill="#ffffff", font=font_bold)
draw.text((2140, 335), "Pin 1 (VCC) : 3.3V (Pin 3V3 NodeMCU)", fill="#f97316", font=font_norm)
draw.text((2140, 375), "Pin 2 (DATA): Pin D5 (GPIO14 NodeMCU)", fill="#a855f7", font=font_norm)
draw.text((2140, 415), "Pin 3 (NC)  : Tidak Dihubungkan", fill="#64748b", font=font_norm)
draw.text((2140, 455), "Pin 4 (GND) : Common Ground", fill="#cbd5e1", font=font_norm)
draw.rounded_rectangle([2135, 495, 2535, 545], radius=6, fill="#0f172a", outline="#eab308")
draw.text((2145, 508), "Catatan: Gunakan R 4.7k-10k pullup", fill="#fbbf24", font=font_small)
draw.text((2145, 526), "antara Pin 1 (VCC) dan Pin 2 (DATA)", fill="#fbbf24", font=font_small)

# ----------------- MODULE 7: LOAD / BEBAN OUTPUT -----------------
load_box = [2120, 600, 2550, 970]
draw_card(load_box, "OUTPUT KE BEBAN / LOAD", header_color="#15803d", border_color="#22c55e")
draw.text((2140, 655), "Terminal Beban Perangkat:", fill="#ffffff", font=font_bold)

draw.rounded_rectangle([2140, 695, 2530, 765], radius=8, fill="#0f172a", outline="#eab308", width=2)
draw.text((2155, 708), "Beban 12V (Hingga 30A)", fill="#eab308", font=font_bold)
draw.text((2155, 735), "Dari IP- ACS712-30A & GND PSU", fill="#cbd5e1", font=font_small)

draw.rounded_rectangle([2140, 785, 2530, 855], radius=8, fill="#0f172a", outline="#ef4444", width=2)
draw.text((2155, 798), "Beban 5V (Hingga 20A)", fill="#ef4444", font=font_bold)
draw.text((2155, 825), "Dari IP- ACS712-20A & GND PSU", fill="#cbd5e1", font=font_small)

draw.rounded_rectangle([2140, 875, 2530, 945], radius=8, fill="#0f172a", outline="#f97316", width=2)
draw.text((2155, 888), "Beban 3.3V (Hingga 10A)", fill="#f97316", font=font_bold)
draw.text((2155, 915), "Dari IP- ACS712-20A & GND PSU", fill="#cbd5e1", font=font_small)

# ----------------- FOOTER INSTRUCTION & PIN SUMMARY TABLE -----------------
table_box = [50, 1190, W - 40, 1750]
draw_card(table_box, "TABEL KONEKSI DETAIL PIN-TO-PIN (ZERO MISTAKE WIRING GUIDE)", header_color="#334155", border_color="#64748b")

cols = [
    ("No", 80),
    ("Nama Sensor / Modul", 450),
    ("Pin Modul", 220),
    ("Tujuan Koneksi (NodeMCU / Modul Lain)", 500),
    ("Fungsi & Catatan Teknis Arus/Voltase", 1200)
]

tx = 70
ty = 1250
draw.rectangle([65, ty, W - 55, ty + 40], fill="#0f172a")
for header, w in cols:
    draw.text((tx, ty + 8), header, fill="#38bdf8", font=font_bold)
    tx += w

connections = [
    ("1", "ACS712 - 30A (Rel 12V)", "IP+ / IP-", "Seri jalur +12V dari PSU ke Beban 12V", "Kabel tebal 10 AWG (30A). VCC=5V, GND=GND, OUT->ADC1 A1 (66mV/A)"),
    ("2", "ACS712 - 20A (Rel 5V)", "IP+ / IP-", "Seri jalur +5V dari PSU ke Beban 5V", "Kabel tebal 12 AWG (20A). VCC=5V, GND=GND, OUT->ADC1 A3 (100mV/A)"),
    ("3", "ACS712 - 20A (Rel 3.3V)", "IP+ / IP-", "Seri jalur +3.3V dari PSU ke Beban 3.3V", "Kabel 16 AWG (10A). VCC=5V, GND=GND, OUT->ADC2 A1 (100mV/A)"),
    ("4", "Sensor Tegangan 12V", "VCC / GND / S", "VCC ke +12V, GND ke Star-GND, S ke ADC1 A0", "Divider 5:1 (Tegangan 12V diturunkan jadi 2.4V maks untuk ADC)"),
    ("5", "Sensor Tegangan 5V", "VCC / GND / S", "VCC ke +5V, GND ke Star-GND, S ke ADC1 A2", "Divider 5:1 (Tegangan 5V diturunkan jadi 1.0V maks untuk ADC)"),
    ("6", "Sensor Tegangan 3.3V", "VCC / GND / S", "VCC ke +3.3V, GND ke Star-GND, S ke ADC2 A0", "Divider 5:1 (Tegangan 3.3V diturunkan jadi 0.66V maks untuk ADC)"),
    ("7", "ADS1115 #1 (Alamat 0x48)", "SCL / SDA / ADDR", "SCL->D1, SDA->D2, ADDR->GND", "VDD=5V, GND=GND. Membaca Tegangan & Arus Rel 12V dan 5V"),
    ("8", "ADS1115 #2 (Alamat 0x49)", "SCL / SDA / ADDR", "SCL->D1, SDA->D2, ADDR->VDD (5V)", "VDD=5V, GND=GND. Membaca Tegangan & Arus Rel 3.3V"),
    ("9", "DHT22 Sensor Suhu/RH", "VCC / DATA / GND", "VCC->3V3 NodeMCU, DATA->D5, GND->GND", "Membaca Suhu Ruang/Power Supply & Kelembaban Udara"),
    ("10", "Ground Bersama (Star-GND)", "Semua GND", "Hubungkan semua titik GND menjadi satu pusat", "PENTING: Mencegah ground loop error & memastikan akurasi pembacaan ADC")
]

row_y = ty + 46
for row in connections:
    bg_row = "#1e293b" if int(row[0]) % 2 == 1 else "#0f172a"
    draw.rectangle([65, row_y, W - 55, row_y + 36], fill=bg_row)
    cur_x = 70
    draw.text((cur_x, row_y + 7), row[0], fill="#fbbf24", font=font_bold)
    cur_x += 80
    draw.text((cur_x, row_y + 7), row[1], fill="#cbd5e1", font=font_bold)
    cur_x += 450
    draw.text((cur_x, row_y + 7), row[2], fill="#38bdf8", font=font_norm)
    cur_x += 220
    draw.text((cur_x, row_y + 7), row[3], fill="#a7f3d0", font=font_norm)
    cur_x += 500
    draw.text((cur_x, row_y + 7), row[4], fill="#fde047", font=font_small)
    row_y += 38

out_path = r"C:\Users\minipingu\Desktop\esp8266_power_monitor\schematics\wiring_diagram.png"
img.save(out_path, "PNG", quality=95)
print(f"Diagram successfully generated at: {out_path}")
