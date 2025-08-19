import os
import json
import shutil
import hashlib
from tkinter import Tk, filedialog
from colorama import init, Fore
import random
import urllib.request
import sys
import time
import pyfiglet

# -------------------------
# Versiyon Kontrol
# -------------------------
CURRENT_VERSION = "1.0.2"
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

red_tones = [Fore.LIGHTRED_EX, Fore.RED]

# -------------------------
# Kullanıcı ASCII Başlığı
# -------------------------
def get_user_id_from_log():
    log_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", ".basonw", "logs", "latest.log")
    user_id = "Bilinmiyor"
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if "Setting user:" in line:
                    user_id = line.strip().split("Setting user:")[-1].strip()
                    break
    except FileNotFoundError:
        pass
    return user_id

def print_user_ascii():
    user_id = get_user_id_from_log()
    ascii_banner = pyfiglet.figlet_format(user_id, font="slant")
    for line in ascii_banner.splitlines():
        colored_line = ""
        for c in line:
            if c.strip() == "":
                colored_line += c
            else:
                color = random.choice(red_tones)
                colored_line += color + c
        print(colored_line)

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
# Mod İşlevleri
# -------------------------
def add_mod():
    os.system("cls")
    print_user_ascii()
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
    print_user_ascii()
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
    print_user_ascii()
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
# Kullanıcı Bilgileri
# -------------------------
def show_user_info():
    os.system("cls")
    print_user_ascii()

    log_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", ".basonw", "logs", "latest.log")
    user_id = "Bilinmiyor"
    password = "Bilinmiyor"

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                if "Setting user:" in line:
                    user_id = line.strip().split("Setting user:")[-1].strip()
                if "Received message:" in line and "|" in line:
                    password = line.strip().split("|")[-1].strip()
    except FileNotFoundError:
        print(Fore.RED + "latest.log dosyası bulunamadı.")
        input("Devam etmek için Enter'a basın...")
        return

    mod_list = os.listdir(moddir)
    total_mods = len(mod_list)
    total_size = sum(os.path.getsize(os.path.join(moddir, m)) for m in mod_list)
    last_check_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    print(Fore.LIGHTRED_EX + f"ID: {user_id}")
    print(Fore.LIGHTRED_EX + f"Şifre: {password}")
    print(Fore.LIGHTRED_EX + f"Versiyon: 1.21.4")
    print(Fore.LIGHTRED_EX + f"Yüklü mod sayısı: {total_mods}")
    print(Fore.LIGHTRED_EX + f"Toplam mod boyutu: {total_size / 1024:.2f} KB")
    print(Fore.LIGHTRED_EX + f"Son güncelleme kontrolü: {last_check_time}")

    input("\nDevam etmek için Enter'a basın...")

# -------------------------
# Launcher Aç
# -------------------------
def open_launcher():
    os.system("cls")
    print_user_ascii()
    launcher_path = r"C:\Users\enesb\AppData\Local\Baso Network\basonw.exe"
    
    if os.path.exists(launcher_path):
        print(Fore.LIGHTRED_EX + "Baso Network launcher açılıyor...")
        os.startfile(launcher_path)
    else:
        print(Fore.RED + "Launcher bulunamadı: " + launcher_path)
    
    input("\nDevam etmek için Enter'a basın...")

# -------------------------
# Menü
# -------------------------
def menu():
    while True:
        os.system("cls")
        print_user_ascii()
        print(Fore.WHITE + "Baso Network Mod Yöneticisi\n")
        print(Fore.RED + "1." + Fore.LIGHTRED_EX + " Mod Ekle")
        print(Fore.RED + "2." + Fore.LIGHTRED_EX + " Mod Sil")
        print(Fore.RED + "3." + Fore.LIGHTRED_EX + " Modları Listele")
        print(Fore.RED + "4." + Fore.LIGHTRED_EX + " Baso Network bilgileri")
        print(Fore.RED + "5." + Fore.LIGHTRED_EX + " Launcherı aç")
        choice = input(Fore.WHITE + "\nSeçiminiz: ")

        if choice == "1":
            add_mod()
        elif choice == "2":
            delete_mod()
        elif choice == "3":
            list_mods()
        elif choice == "4":
            show_user_info()
        elif choice == "5":
            open_launcher()
        else:
            print(Fore.LIGHTRED_EX + "Geçersiz seçim.")
            input("Devam etmek için Enter'a basın...")

# -------------------------
# Başlat
# -------------------------
if __name__ == "__main__":
    check_update()
    menu()
