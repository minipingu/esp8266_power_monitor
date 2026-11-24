# DAFTAR HARGA KOMPONEN & ESTIMASI BIAYA PROYEK (RAB)
## Proyek ESP8266 Multi-Rail Power Supply Monitor (12V/30A, 5V/20A, 3.3V/10A + DHT22)

Harga di bawah ini merupakan referensi harga pasaran e-commerce Indonesia (**Tokopedia** & **Shopee**) per November 2026 dari toko-toko komponen elektronik populer (seperti *CNC Store, Depok Elektro, Digiware, Rajacell, dll.*).

---

## 1. Tabel Rincian Biaya Komponen Utama (BOM)

| No | Nama Komponen & Deskripsi | Qty | Kisaran Harga Satuan | Subtotal Estimasi | Catatan Pembelian |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | **NodeMCU ESP8266 V3 (ESP-12E)**<br>Mikrokontroler IoT WiFi (CH340/CP2102) | 1 pcs | Rp 38.000 – Rp 50.000 | **Rp 42.000** | Pilih tipe NodeMCU V3 Lolin atau Amica |
| **2** | **Modul ADS1115 16-Bit 4-Channel ADC**<br>ADC presisi tinggi I2C (Alamat 0x48 & 0x49) | 2 pcs | Rp 28.000 – Rp 38.000 | **Rp 66.000** | 1 modul untuk 12V & 5V, 1 modul untuk 3.3V |
| **3** | **Modul Sensor Arus ACS712 - 30A**<br>Sensor Hall-Effect rel 12V (Sensitivitas 66 mV/A) | 1 pcs | Rp 18.000 – Rp 25.000 | **Rp 20.000** | Wajib untuk rel 12V beban hingga 30A |
| **4** | **Modul Sensor Arus ACS712 - 20A**<br>Sensor Hall-Effect (Sensitivitas 100 mV/A) | 2 pcs | Rp 17.000 – Rp 24.000 | **Rp 38.000** | 1 pcs untuk rel 5V (20A) & 1 pcs untuk 3.3V (10A) |
| **5** | **Modul Sensor Tegangan DC 0–25V**<br>Resistor divider 5:1 (30kΩ & 7.5kΩ) | 3 pcs | Rp 4.500 – Rp 6.500 | **Rp 15.000** | Masing-masing untuk rel 12V, 5V, dan 3.3V |
| **6** | **Sensor Suhu & Kelembaban DHT22 (AM2302)**<br>Sensor digital presisi tinggi (Pin D5) | 1 pcs | Rp 28.000 – Rp 40.000 | **Rp 32.000** | Rekomendasi versi PCB modul yang sudah ada resistor |
| **TOTAL KOMPONEN UTAMA** | | | | **Rp 213.000** | *(Estimasi nilai tengah)* |

---

## 2. Tabel Komponen Pendukung, Kabel Extension ATX & PCIe

| No | Material Pendukung & Kabel Extension | Qty | Kisaran Harga Satuan | Estimasi Biaya | Keterangan & Fungsi |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | **Kabel Extension ATX 24-Pin (Female to Male)**<br>Standar 30 cm 18 AWG | 1 pcs | Rp 25.000 – Rp 45.000 | **Rp 32.000** | Dipotong untuk rel 5V, 3.3V, dan tap GND |
| **2** | **Kabel Extension PCIe 8-Pin / 6+2 (Female to Male)**<br>Standar 30 cm 18 AWG | 1 pcs | Rp 20.000 – Rp 35.000 | **Rp 25.000** | Dipotong kawat kuning untuk rel 12V (30A) |
| **3** | **Kabel Jumper DuPont (Female-to-Female & Male)** | 1 set (40 pcs) | Rp 8.000 – Rp 12.000 | **Rp 10.000** | Kabel sinyal logika I2C & sensor ADC |
| **4** | **PCB Lubang Matrix (Donat) 7x9 cm** | 1 pcs | Rp 4.000 – Rp 7.000 | **Rp 5.000** | Baseboard untuk merapikan modul & Star-GND |
| **5** | **Isolasi Bakar (Heat Shrink Tubing) 3mm & 6mm** | 1 set | Rp 6.000 – Rp 10.000 | **Rp 8.000** | Membungkus aman sambungan kawat extension |
| **TOTAL KABEL EXTENSION & PENDUKUNG** | | | | **Rp 80.000** | *(Metode Plug-and-Play tanpa potong kabel PSU)* |

---

## 3. Ringkasan Total Anggaran Proyek (RAB)

| Kategori | Estimasi Terendah | Estimasi Rata-rata | Estimasi Tertinggi |
| :--- | :---: | :---: | :---: |
| **Komponen Elektronika Utama** | Rp 175.000 | **Rp 213.000** | Rp 250.000 |
| **Kabel Extension ATX & PCIe + Pendukung** | Rp 63.000 | **Rp 80.000** | Rp 107.000 |
| **TOTAL ANGGARAN LENGKAP** | **Rp 238.000** | **Rp 293.000** | **Rp 357.000** |

---

## 4. Opsi Alternatif Hemat Biaya (Cost-Down Options)

1. **Ganti DHT22 dengan DHT11:**
   - DHT11 dijual seharga **Rp 10.000 – Rp 13.000** (hemat $\approx$ Rp 20.000).
   - *Catatan:* Rentang pembacaan DHT11 lebih sempit (0–50°C, 20–90% RH) dibanding DHT22 (-40 s.d. 80°C, 0–100% RH).
2. **Merakit Sendiri Pembagi Tegangan (Resistor Satuan):**
   - Menggunakan 6 buah resistor biasa (3 buah $30\text{ k}\Omega$ + 3 buah $7.5\text{ k}\Omega$ metal film 1%).
   - Biaya resistor satuan hanya sekitar **Rp 500 – Rp 1.000** per paket (hemat $\approx$ Rp 12.000).
3. **Menggunakan Kabel PSU Bekas:**
   - Jika Anda memiliki power supply ATX komputer bekas, kabel kuning (12V), merah (5V), oranye (3.3V), dan hitam (GND) bawaan PSU dapat langsung dimanfaatkan sehingga tidak perlu membeli kabel silikon baru (hemat $\approx$ Rp 50.000).
