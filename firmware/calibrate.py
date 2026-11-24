"""
Zero-Current Auto-Calibration Script for ACS712 Sensors
Run this script while NO LOAD is connected to zero-out the current sensors.
It automatically updates 'config.json' with calibrated zero-point voltages.
"""
from machine import Pin, I2C
import time
import ujson
from ads1115 import ADS1115, PGA_6_144V

def calibrate():
    print("==================================================")
    print("   ACS712 ZERO-CURRENT SENSOR CALIBRATION TOOL    ")
    print("==================================================")
    print("PENTING: Pastikan TIDAK ADA BEBAN (Zero Amps) yang")
    print("mengalir pada jalur 12V, 5V, dan 3.3V saat ini!\n")
    
    with open("config.json", "r") as f:
        cfg = ujson.load(f)

    hw = cfg.get("hardware", {})
    i2c = I2C(scl=Pin(hw.get("i2c_scl_pin", 5)), sda=Pin(hw.get("i2c_sda_pin", 4)), freq=400000)

    adc1 = ADS1115(i2c, address=hw.get("adc1_i2c_addr", 0x48), pga=PGA_6_144V)
    adc2 = ADS1115(i2c, address=hw.get("adc2_i2c_addr", 0x49), pga=PGA_6_144V)

    print("Memulai pengambilan 100 sampel tegangan baseline nol...")
    samples = 100
    sum_i12, sum_i5, sum_i33 = 0.0, 0.0, 0.0

    for i in range(samples):
        sum_i12 += adc1.read_voltage(1, samples=2)
        sum_i5  += adc1.read_voltage(3, samples=2)
        sum_i33 += adc2.read_voltage(1, samples=2)
        if (i + 1) % 20 == 0:
            print(f"Progress: {i + 1}/{samples} sampel...")
        time.sleep_ms(20)

    avg_12 = sum_i12 / samples
    avg_5  = sum_i5 / samples
    avg_33 = sum_i33 / samples

    print("\nHASIL KALIBRASI TEGANGAN BASELINE NOL (V_zero):")
    print(f"12V ACS712-30A Baseline : {avg_12:.4f} Volt (Ideal: 2.5000V)")
    print(f"5V  ACS712-20A Baseline : {avg_5:.4f} Volt (Ideal: 2.5000V)")
    print(f"3.3V ACS712-20A Baseline: {avg_33:.4f} Volt (Ideal: 2.5000V)")

    cfg["calibration"]["rail_12v"]["i_zero_volts"] = round(avg_12, 4)
    cfg["calibration"]["rail_5v"]["i_zero_volts"]  = round(avg_5, 4)
    cfg["calibration"]["rail_3v3"]["i_zero_volts"] = round(avg_33, 4)

    with open("config.json", "w") as f:
        ujson.dump(cfg, f)

    print("\n[SUKSES] Konfigurasi config.json berhasil diperbarui!")
    print("Nilai offset baru akan langsung digunakan saat sistem di-restart.\n")

if __name__ == "__main__":
    calibrate()
