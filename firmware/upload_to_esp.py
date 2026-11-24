"""
Automated Firmware Flasher for ESP8266 using mpremote.
Uploads boot.py, main.py, config.json, ads1115.py, and calibrate.py.
"""
import subprocess
import sys
import os

FILES_TO_UPLOAD = [
    "config.json",
    "ads1115.py",
    "boot.py",
    "main.py",
    "calibrate.py"
]

def main():
    print("==================================================")
    print("  ESP8266 MICROPYTHON FIRMWARE UPLOADER (MPREMOTE) ")
    print("==================================================")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 1. Check mpremote
    try:
        res = subprocess.run(["mpremote", "connect", "list"], capture_ok=True, text=True, check=False)
        print("[1] Memeriksa perangkat ESP8266 yang tersambung...")
    except Exception as e:
        print("[!] Error menjalankan mpremote:", e)
        return

    # 2. Upload files
    for filename in FILES_TO_UPLOAD:
        if not os.path.exists(filename):
            print(f"[!] File {filename} tidak ditemukan, dilewati.")
            continue
        print(f"[*] Mengunggah {filename} ke ESP8266...")
        cmd = ["mpremote", "fs", "cp", filename, f":{filename}"]
        res = subprocess.run(cmd, check=False)
        if res.returncode == 0:
            print(f"    [OK] {filename} berhasil diunggah.")
        else:
            print(f"    [GAGAL] Tidak dapat mengunggah {filename}.")

    print("\n[+] Menguji soft-reset ESP8266...")
    subprocess.run(["mpremote", "reset"], check=False)
    print("\n[SUKSES] Semua file firmware telah diunggah ke ESP8266!")

if __name__ == "__main__":
    main()
