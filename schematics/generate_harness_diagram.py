"""
Script to generate ultra-clear, high-resolution ATX 24-Pin & PCIe Extension
Harness Cut-and-Breakout Wiring Diagram PNG.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 2600, 1900
img = Image.new("RGB", (W, H), color="#0f172a")
draw = ImageDraw.Draw(img)

try:
    font_title = ImageFont.truetype("arialbd.ttf", 44)
    font_sub = ImageFont.truetype("arial.ttf", 24)
    font_box_title = ImageFont.truetype("arialbd.ttf", 26)
    font_bold = ImageFont.truetype("arialbd.ttf", 22)
    font_norm = ImageFont.truetype("arial.ttf", 20)
    font_small = ImageFont.truetype("arial.ttf", 17)
    font_mono = ImageFont.truetype("consola.ttf", 19)
except Exception:
    font_title = font_sub = font_box_title = font_bold = font_norm = font_small = font_mono = ImageFont.load_default()

# ----------------- HEADER -----------------
draw.rounded_rectangle([40, 30, W - 40, 130], radius=16, fill="#1e293b", outline="#334155", width=3)
draw.text((70, 48), "PANDUAN WIRING HARNESS: KABEL EXTENSION ATX 24-PIN & PCIE (FEMALE TO MALE)", fill="#38bdf8", font=font_title)
draw.text((70, 100), "Metode Pemotongan Jalur Extension Tanpa Merusak Kabel Asli PSU | Pasang Seri ke Sensor ACS712", fill="#94a3b8", font=font_sub)

# ----------------- HELPER FUNCTIONS -----------------
def draw_card(box, title, header_color="#334155", border_color="#475569", bg="#1e293b"):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=12, fill=bg, outline=border_color, width=2)
    draw.rounded_rectangle([x0, y0, x1, y0 + 44], radius=12, fill=header_color)
    draw.rectangle([x0, y0 + 20, x1, y0 + 44], fill=header_color)
    draw.text((x0 + 16, y0 + 10), title, fill="#ffffff", font=font_box_title)

# ----------------- COLUMN 1: FEMALE CONNECTORS (INPUT FROM PSU) -----------------
# 1. ATX 24-Pin Female
box_atx_f = [50, 160, 480, 880]
draw_card(box_atx_f, "ATX 24-PIN EXTENDER (FEMALE)", header_color="#0369a1", border_color="#0284c7")
draw.text((70, 215), "Dicolokkan ke Kabel Asli PSU", fill="#38bdf8", font=font_bold)
draw.text((70, 245), "Pemetaan Kawat Warna:", fill="#cbd5e1", font=font_norm)

atx_pins = [
    ("Oranye (+3.3V)", "Pin 1, 2, 12, 13 (4 Kawat)", "#f97316", 280),
    ("Merah (+5V)", "Pin 4, 6, 21, 22, 23 (5 Kawat)", "#ef4444", 390),
    ("Kuning (+12V Mobo)", "Pin 10, 11 (2 Kawat)", "#eab308", 500),
    ("Hitam (GND)", "Pin 3, 5, 7, 15, 17, 18, 19, 24", "#94a3b8", 610),
    ("Kawat Kontrol", "Hijau(PS_ON), Abu(PWR_OK), Ungu(5VSB)", "#a855f7", 720)
]
for p_title, p_desc, col, y in atx_pins:
    draw.rounded_rectangle([70, y, 460, y + 80], radius=8, fill="#0f172a", outline=col, width=2)
    draw.text((85, y + 14), p_title, fill=col, font=font_bold)
    draw.text((85, y + 44), p_desc, fill="#cbd5e1", font=font_small)

# 2. PCIe 8-Pin Female (For 12V 30A Heavy Load)
box_pcie_f = [50, 920, 480, 1320]
draw_card(box_pcie_f, "PCIE 8-PIN EXTENDER (FEMALE)", header_color="#854d0e", border_color="#eab308")
draw.text((70, 975), "Jalur Beban Berat 12V (Hingga 30A)", fill="#fbbf24", font=font_bold)

pcie_pins = [
    ("Kuning (+12V DC)", "Pin 1, 2, 3 (3 Kawat 18 AWG)", "#eab308", 1015),
    ("Hitam (Ground / Sense)", "Pin 4, 5, 6, 7, 8 (5 Kawat)", "#94a3b8", 1125),
    ("Kapasitas Total", "3 Kawat 18 AWG Gabungan = ~30A", "#fbbf24", 1235)
]
for p_title, p_desc, col, y in pcie_pins:
    draw.rounded_rectangle([70, y, 460, y + 75], radius=8, fill="#0f172a", outline=col, width=2)
    draw.text((85, y + 12), p_title, fill=col, font=font_bold)
    draw.text((85, y + 42), p_desc, fill="#cbd5e1", font=font_small)

# ----------------- COLUMN 2: POTONG & INTERCEPT KE SENSOR (TENGAH) -----------------
# 1. Intercept 12V 30A
box_cut_12 = [580, 160, 1180, 490]
draw_card(box_cut_12, "INTERCEPT JALUR 12V (ACS712-30A)", header_color="#854d0e", border_color="#eab308")
draw.text((600, 215), "1. Potong kawat Kuning (+12V) di tengah extender.", fill="#ffffff", font=font_bold)
draw.text((600, 245), "2. Satukan (twist/krimping ferrule) kawat kuning dari sisi Female,", fill="#eab308", font=font_norm)
draw.text((600, 275), "   lalu masukkan dan kencangkan ke baut IP+ ACS712-30A.", fill="#eab308", font=font_norm)
draw.text((600, 310), "3. Satukan kawat kuning dari baut IP- ACS712-30A,", fill="#eab308", font=font_norm)
draw.text((600, 340), "   lalu sambungkan menuju konektor Male.", fill="#eab308", font=font_norm)
draw.text((600, 380), "[TAP TEGANGAN]: Kupas sedikit kawat 12V, pasang kabel tipis", fill="#38bdf8", font=font_bold)
draw.text((600, 410), "menuju pin VCC/S modul Voltage Sensor 12V (divider 5:1).", fill="#38bdf8", font=font_norm)
draw.text((600, 445), "Sinyal ACS712 OUT -> Pin A1 pada ADS1115 #1 (Addr 0x48)", fill="#22c55e", font=font_bold)

# 2. Intercept 5V 20A
box_cut_5 = [580, 520, 1180, 850]
draw_card(box_cut_5, "INTERCEPT JALUR 5V (ACS712-20A)", header_color="#991b1b", border_color="#ef4444")
draw.text((600, 575), "1. Potong semua kawat Merah (+5V) di tengah extender 24-Pin.", fill="#ffffff", font=font_bold)
draw.text((600, 605), "2. Satukan 5 kawat merah dari sisi Female ke IP+ ACS712-20A.", fill="#ef4444", font=font_norm)
draw.text((600, 635), "3. Sambungkan IP- ACS712-20A ke 5 kawat merah sisi Male.", fill="#ef4444", font=font_norm)
draw.text((600, 675), "[TAP TEGANGAN]: Ambil cabang kabel tipis dari kawat merah", fill="#38bdf8", font=font_bold)
draw.text((600, 705), "menuju pin VCC/S modul Voltage Sensor 5V (divider 5:1).", fill="#38bdf8", font=font_norm)
draw.text((600, 745), "Sinyal ACS712 OUT -> Pin A3 pada ADS1115 #1 (Addr 0x48)", fill="#22c55e", font=font_bold)
draw.text((600, 785), "Gunakan isolasi bakar (heat shrink) pada sambungan!", fill="#fbbf24", font=font_small)

# 3. Intercept 3.3V 10A
box_cut_33 = [580, 880, 1180, 1210]
draw_card(box_cut_33, "INTERCEPT JALUR 3.3V (ACS712-20A)", header_color="#9a3412", border_color="#f97316")
draw.text((600, 935), "1. Potong semua kawat Oranye (+3.3V) di tengah extender 24-Pin.", fill="#ffffff", font=font_bold)
draw.text((600, 965), "2. Satukan 4 kawat oranye dari sisi Female ke IP+ ACS712-20A.", fill="#f97316", font=font_norm)
draw.text((600, 995), "3. Sambungkan IP- ACS712-20A ke 4 kawat oranye sisi Male.", fill="#f97316", font=font_norm)
draw.text((600, 1035), "[TAP TEGANGAN]: Ambil cabang kabel tipis dari kawat oranye", fill="#38bdf8", font=font_bold)
draw.text((600, 1065), "menuju pin VCC/S modul Voltage Sensor 3.3V (divider 5:1).", fill="#38bdf8", font=font_norm)
draw.text((600, 1105), "Sinyal ACS712 OUT -> Pin A1 pada ADS1115 #2 (Addr 0x49)", fill="#22c55e", font=font_bold)
draw.text((600, 1145), "Kabel pin 13 (sense) tetap ikut digabung.", fill="#cbd5e1", font=font_small)

# 4. Kawat Kontrol & Ground (JANGAN DIPOTONG!)
box_ctrl = [580, 1240, 1180, 1490]
draw_card(box_ctrl, "KAWAT KONTROL & GROUND (LEWAT LANGSUNG)", header_color="#334155", border_color="#64748b")
draw.text((600, 1295), "• Kawat Hitam (GND): JANGAN diputus! Lewat langsung Female ke Male.", fill="#cbd5e1", font=font_norm)
draw.text((600, 1325), "  Cukup kupas sedikit jaket kawat untuk mengambil cabang (Tap)", fill="#cbd5e1", font=font_norm)
draw.text((600, 1355), "  ke titik Star-Ground ESP8266 & Modul ADS1115.", fill="#38bdf8", font=font_bold)
draw.text((600, 1395), "• Kawat Kontrol ATX: Hijau (PS_ON), Abu (PWR_OK), Ungu (5VSB)", fill="#c084fc", font=font_bold)
draw.text((600, 1425), "  BIARKAN UTUH TERHUBUNG LURUS agar PSU dapat menyala normal!", fill="#f87171", font=font_bold)

# ----------------- COLUMN 3: MALE CONNECTORS (OUTPUT TO PC/LOAD) -----------------
# 1. ATX 24-Pin Male
box_atx_m = [1280, 160, 1710, 880]
draw_card(box_atx_m, "ATX 24-PIN EXTENDER (MALE)", header_color="#0369a1", border_color="#0284c7")
draw.text((1300, 215), "Dicolokkan ke Motherboard PC", fill="#38bdf8", font=font_bold)
draw.text((1300, 245), "Menerima Arus dari Sensor:", fill="#cbd5e1", font=font_norm)

atx_m_pins = [
    ("Oranye (+3.3V)", "Menerima dari IP- ACS712-20A (Pin 1, 2, 12, 13)", "#f97316", 280),
    ("Merah (+5V)", "Menerima dari IP- ACS712-20A (Pin 4, 6, 21, 22, 23)", "#ef4444", 390),
    ("Kuning (+12V Mobo)", "Menerima dari IP- ACS712 (Pin 10, 11)", "#eab308", 500),
    ("Hitam (GND)", "Terhubung lurus langsung dari PSU", "#94a3b8", 610),
    ("Kawat Kontrol", "Hijau, Abu, Ungu terhubung utuh langsung", "#a855f7", 720)
]
for p_title, p_desc, col, y in atx_m_pins:
    draw.rounded_rectangle([1300, y, 1690, y + 80], radius=8, fill="#0f172a", outline=col, width=2)
    draw.text((1315, y + 14), p_title, fill=col, font=font_bold)
    draw.text((1315, y + 44), p_desc, fill="#cbd5e1", font=font_small)

# 2. PCIe 8-Pin Male (To Graphics Card / High Current Load)
box_pcie_m = [1280, 920, 1710, 1320]
draw_card(box_pcie_m, "PCIE 8-PIN EXTENDER (MALE)", header_color="#854d0e", border_color="#eab308")
draw.text((1300, 975), "Dicolokkan ke Kartu Grafis (GPU) / Beban", fill="#fbbf24", font=font_bold)

pcie_m_pins = [
    ("Kuning (+12V DC)", "Menerima dari IP- ACS712-30A (Pin 1, 2, 3)", "#eab308", 1015),
    ("Hitam (Ground)", "Terhubung lurus langsung dari PSU", "#94a3b8", 1125),
    ("Status Beban", "Arus beban GPU terpantau penuh hingga 30A", "#fbbf24", 1235)
]
for p_title, p_desc, col, y in pcie_m_pins:
    draw.rounded_rectangle([1300, y, 1690, y + 75], radius=8, fill="#0f172a", outline=col, width=2)
    draw.text((1315, y + 12), p_title, fill=col, font=font_bold)
    draw.text((1315, y + 42), p_desc, fill="#cbd5e1", font=font_small)

# ----------------- COLUMN 4: SISTEM SENSOR & MIKROKONTROLER (KANAN) -----------------
box_esp = [1810, 160, 2550, 1490]
draw_card(box_esp, "BLOK PEMROSES DATA & I2C SENSOR", header_color="#1d4ed8", border_color="#3b82f6")

draw.text((1835, 220), "ARSITEKTUR PEMBACAAN DUAL ADS1115:", fill="#ffffff", font=font_bold)

# ADC 1 Card
draw.rounded_rectangle([1835, 260, 2525, 540], radius=10, fill="#0f172a", outline="#06b6d4", width=2)
draw.text((1855, 275), "ADS1115 #1 (Alamat I2C: 0x48 | Pin ADDR -> GND)", fill="#06b6d4", font=font_bold)
draw.text((1855, 315), "• A0: Sensor Tegangan 12V (Divider 5:1 dari tap kawat kuning)", fill="#eab308", font=font_norm)
draw.text((1855, 355), "• A1: Sinyal OUT Sensor Arus ACS712-30A (Rel 12V)", fill="#eab308", font=font_norm)
draw.text((1855, 395), "• A2: Sensor Tegangan 5V (Divider 5:1 dari tap kawat merah)", fill="#ef4444", font=font_norm)
draw.text((1855, 435), "• A3: Sinyal OUT Sensor Arus ACS712-20A (Rel 5V)", fill="#ef4444", font=font_norm)
draw.text((1855, 480), "I2C Bus: SCL -> Pin D1 | SDA -> Pin D2 NodeMCU", fill="#cbd5e1", font=font_small)

# ADC 2 Card
draw.rounded_rectangle([1835, 560, 2525, 840], radius=10, fill="#0f172a", outline="#06b6d4", width=2)
draw.text((1855, 575), "ADS1115 #2 (Alamat I2C: 0x49 | Pin ADDR -> VDD)", fill="#06b6d4", font=font_bold)
draw.text((1855, 615), "• A0: Sensor Tegangan 3.3V (Divider 5:1 dari tap kawat oranye)", fill="#f97316", font=font_norm)
draw.text((1855, 655), "• A1: Sinyal OUT Sensor Arus ACS712-20A (Rel 3.3V)", fill="#f97316", font=font_norm)
draw.text((1855, 695), "• A2 & A3: Cadangan / Spare Channel", fill="#64748b", font=font_norm)
draw.text((1855, 740), "I2C Bus: Paralel dengan ADS1115 #1 (SCL D1, SDA D2)", fill="#cbd5e1", font=font_small)

# DHT22 Card
draw.rounded_rectangle([1835, 860, 2525, 1080], radius=10, fill="#0f172a", outline="#a855f7", width=2)
draw.text((1855, 875), "SENSOR SUHU & KELEMBABAN (DHT22)", fill="#a855f7", font=font_bold)
draw.text((1855, 915), "• Pin Data -> Hubungkan ke NodeMCU Pin D5 (GPIO 14)", fill="#c084fc", font=font_norm)
draw.text((1855, 955), "• Pin VCC  -> Pin 3V3 NodeMCU", fill="#f8fafc", font=font_norm)
draw.text((1855, 995), "• Pin GND  -> Common Ground", fill="#94a3b8", font=font_norm)
draw.text((1855, 1035), "• R Pull-up 4.7k-10kΩ antara VCC dan DATA", fill="#fbbf24", font=font_small)

# NodeMCU Card
draw.rounded_rectangle([1835, 1100, 2525, 1460], radius=10, fill="#0f172a", outline="#3b82f6", width=2)
draw.text((1855, 1115), "ESP8266 NODEMCU CONTROLLER", fill="#38bdf8", font=font_bold)
draw.text((1855, 1155), "• Daya VIN: Mengambil suplai 5V dari tap kawat merah extender", fill="#ef4444", font=font_norm)
draw.text((1855, 1195), "• Ground  : Terhubung ke Star-Ground kabel hitam extender", fill="#cbd5e1", font=font_norm)
draw.text((1855, 1235), "• Web Dashboard: Akses langsung via IP WiFi http://<ip_esp>/", fill="#38bdf8", font=font_norm)
draw.text((1855, 1275), "• Telemetri Serial: Kirim JSON per detik ke Desktop App via USB", fill="#38bdf8", font=font_norm)
draw.text((1855, 1315), "• Aman & Rapi: Kabel PSU asli 100% utuh tanpa lecet garansi!", fill="#22c55e", font=font_bold)

# ----------------- FOOTER PETUNJUK TEKNIS -----------------
draw.rounded_rectangle([50, 1520, W - 40, 1860], radius=12, fill="#1e293b", outline="#e11d48", width=2)
draw.text((70, 1545), "PETUNJUK TEKNIS PEMASANGAN KABEL EXTENSION (ZERO RISK & ZERO MISTAKE):", fill="#f43f5e", font=font_bold)

tips = [
    ("1. PENGGABUNGAN KAWAT PARALEL:", "Pada ATX 24-Pin, terdapat 4 kawat oranye (3.3V) dan 5 kawat merah (5V). Semua kawat oranye dari sisi Female HARUS digabung jadi 1 bundel ke terminal IP+ sensor, lalu dari IP- dihubungkan ke 4 kawat oranye sisi Male. Hal ini agar arus terdistribusi merata dan tidak ada kawat yang kelebihan beban."),
    ("2. KAWAT 12V 30A (PCIE EXTENDER):", "Pada PCIe 8-Pin terdapat 3 kawat kuning (+12V 18 AWG). Gabung ketiga kawat kuning ke IP+ ACS712-30A. Kencangkan baut terminal sekuat mungkin atau gunakan ferrule crimp."),
    ("3. KAWAT KONTROL ATX TETAP UTUH:", "Jangan potong kawat hijau (PS_ON), abu-abu (PWR_OK), dan ungu (5VSB). Kawat ini mengontrol logika penyalaan motherboard PC. Biarkan langsung terhubung dari Female ke Male."),
    ("4. STAR GROUNDING & VOLTAGE TAP:", "Kawat hitam (GND) biarkan lurus dari Female ke Male. Cukup kupas 5mm jaket kawat hitam untuk menyolder 1 kabel tap ground ke ESP8266 & ADS1115. Demikian juga untuk modul sensor tegangan, cukup tap kabel kecil 24 AWG dari jalur 12V, 5V, dan 3.3V.")
]
ty = 1585
for title, desc in tips:
    draw.text((70, ty), title, fill="#fbbf24", font=font_bold)
    draw.text((380, ty + 2), desc[:150], fill="#e2e8f0", font=font_small)
    if len(desc) > 150:
        draw.text((380, ty + 24), desc[150:], fill="#e2e8f0", font=font_small)
    ty += 64

out_harness = r"C:\Users\minipingu\Desktop\esp8266_power_monitor\schematics\atx_pcie_harness_diagram.png"
img.save(out_harness, "PNG", quality=95)
print(f"Harness diagram successfully generated at: {out_harness}")
