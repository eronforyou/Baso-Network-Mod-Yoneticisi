import os
import json
import shutil
import hashlib
from tkinter import Tk, filedialog
from colorama import init, Fore
import random
import urllib.request
import sys

# -------------------------
# Versiyon Kontrol
# -------------------------
CURRENT_VERSION = "1.0.1"
VERSION_URL = "https://raw.githubusercontent.com/eronforyou/Baso-Network-Mod-Yoneticisi/refs/heads/main/version.txt"
SCRIPT_URL  = "https://raw.githubusercontent.com/eronforyou/Baso-Network-Mod-Yoneticisi/refs/heads/main/BNWModYoneticisi.py"
SCRIPT_PATH = os.path.realpath(__file__)

def check_update():
    try:
        with urllib.request.urlopen(VERSION_URL) as response:
            latest_version = response.read().decode("utf-8").strip()
        if latest_version != CURRENT_VERSION:
            print(f"Yeni sürüm bulundu: {latest_version} (Sizin sürüm: {CURRENT_VERSION})")
            print("Güncelleme indiriliyor...")
            with urllib.request.urlopen(SCRIPT_URL) as response:
                new_script = response.read()
            with open(SCRIPT_PATH, "wb") as f:
                f.write(new_script)
            print("Güncelleme tamamlandı! Lütfen programı tekrar başlatın.")
            sys.exit()
        else:
            print(f"Sürüm güncel: {CURRENT_VERSION}")
    except Exception as e:
        print(f"Versiyon kontrolü yapılamadı: {e}")

# -------------------------
# Başlangıç ayarları
# -------------------------
init(autoreset=True)
jsonfile = r"C:\xampp\htdocs\files"
moddir = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", ".basonw", "mods")
os.makedirs(moddir, exist_ok=True)

# Kırmızı tonları listesi (sadece kırmızı)
red_tones = [Fore.LIGHTRED_EX, Fore.RED]

# -------------------------
# Yardımcı Fonksiyonlar
# -------------------------
def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha1.update(chunk)
    return sha1.hexdigest()

def load_json():
    if os.path.exists(jsonfile):
        with open(jsonfile, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(data):
    json_text = "[\n"
    for i, m in enumerate(data):
        json_text += "  " + json.dumps(m, ensure_ascii=False, indent=2).replace("\n", "\n  ")
        if i < len(data) - 1:
            json_text += ","
        json_text += "\n"
    json_text += "]\n"
    with open(jsonfile, "w", encoding="utf-8") as f:
        f.write(json_text)

# -------------------------
# ASCII Başlık
# -------------------------
ascii_text = r"""
                                         /$$   /$$          
                                        | $$  | $$          
  /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$$ | $$  | $$ /$$   /$$
 /$$__  $$ /$$__  $$ /$$__  $$| $$__  $$| $$$$$$$$| $$  | $$ 
| $$$$$$$$| $$  \__/| $$  \ $$| $$  \ $$|_____  $$| $$  | $$
| $$_____/| $$      | $$  | $$| $$  | $$      | $$| $$  | $$
|  $$$$$$$| $$      |  $$$$$$/| $$  | $$      | $$|  $$$$$$/ 
 \_______/|__/       \______/ |__/  |__/      |__/ \______/ 

"""

def print_colored_ascii(ascii_text):
    for line in ascii_text.splitlines():
        out = ""
        for c in line:
            if c.strip() == "":
                out += c
            else:
                color = random.choice(red_tones)
                out += color + c
        print(out)

# -------------------------
# Mod İşlevleri
# -------------------------
def add_mod():
    os.system("cls")
    print_colored_ascii(ascii_text)
    Tk().withdraw()
    file_path = filedialog.askopenfilename(title="Lütfen eklenecek dosyayı seçin")
    if not file_path:
        print(Fore.LIGHTRED_EX + "Dosya seçilmedi.")
        input("Devam etmek için Enter'a basın...")
        return

    filename = os.path.basename(file_path)
    target_path = os.path.join(moddir, filename)
    shutil.copy2(file_path, target_path)
    filesize = os.path.getsize(target_path)
    sha1 = calculate_sha1(target_path)

    mods = load_json()
    mods.append({
        "name": filename,
        "size": filesize,
        "sha1": sha1,
        "download_link": f"/download/mods/{filename}",
        "path": f"mods/{filename}"
    })
    save_json(mods)
    print(Fore.LIGHTRED_EX + f"Mod eklendi: {filename}")
    input("Devam etmek için Enter'a basın...")

def list_mods():
    os.system("cls")
    print_colored_ascii(ascii_text)
    mods = os.listdir(moddir)
    print(Fore.LIGHTRED_EX + "Mods klasöründeki modlar:\n")
    if not mods:
        print(Fore.RED + "Hiç mod bulunamadı.")
    else:
        colors = [Fore.RED, Fore.LIGHTRED_EX]
        for i, m in enumerate(mods):
            color = colors[i % 2]
            print(color + f" - {m}")
    input("\nDevam etmek için Enter'a basın...")

def delete_mod():
    os.system("cls")
    print_colored_ascii(ascii_text)
    mods = os.listdir(moddir)
    if not mods:
        print(Fore.RED + "Hiç mod bulunamadı.")
        input("Devam etmek için Enter'a basın...")
        return

    print(Fore.LIGHTRED_EX + "Silinecek mod seçin:\n")
    colors = [Fore.RED, Fore.LIGHTRED_EX]
    for i, m in enumerate(mods, 1):
        color_number = colors[(i-1) % 2]
        color_name = colors[i % 2]
        print(color_number + f"{i}." + color_name + f" {m}")

    choice = input(Fore.LIGHTRED_EX + "\nNumara girin: ")
    if not choice.isdigit() or not (1 <= int(choice) <= len(mods)):
        print(Fore.LIGHTRED_EX + "Geçersiz seçim.")
        input("Devam etmek için Enter'a basın...")
        return

    modname = mods[int(choice)-1]
    os.remove(os.path.join(moddir, modname))

    data = load_json()
    data = [m for m in data if m["name"] != modname]
    save_json(data)

    print(Fore.LIGHTRED_EX + f"Mod silindi: {modname}")
    input("Devam etmek için Enter'a basın...")

# -------------------------
# Menü
# -------------------------
def menu():
    while True:
        os.system("cls")
        print_colored_ascii(ascii_text)
        print(Fore.WHITE + "                Baso Network Mod Yöneticisi")
        print("")
        print(Fore.RED + "1." + Fore.LIGHTRED_EX + " Mod Ekle")
        print(Fore.RED + "2." + Fore.LIGHTRED_EX + " Mod Sil")
        print(Fore.RED + "3." + Fore.LIGHTRED_EX + " Modları Listele")
        choice = input(Fore.WHITE + "\nSeçiminiz: ")

        if choice == "1":
            add_mod()
        elif choice == "2":
            delete_mod()
        elif choice == "3":
            list_mods()
        else:
            print(Fore.LIGHTRED_EX + "Geçersiz seçim.")
            input("Devam etmek için Enter'a basın...")

# -------------------------
# Başlat
# -------------------------
if __name__ == "__main__":
    check_update()
    menu()
