# ================ IMPORT GLOBAL ===================
import os
import sys
import time
import json
import base64
import requests
import subprocess
import threading
import urllib3
import pyperclip
import platform
import webbrowser
import re
import random
import platform
import sys
import shutil
import subprocess
import datetime
import pytz
import select
import socket
from termcolor import colored
from datetime import datetime, timedelta, timezone
from datetime import datetime, timezone, timedelta
from colorama import Fore, Style, init
from urllib.parse import urlparse
init(autoreset=True)
import sys
import platform

DEBUG_MODE = False
def debug_print(*args, **kwargs):
    if DEBUG_MODE:
        print("[DEBUG]", *args, **kwargs)
        
# **** Warna Global ****
green = Fore.GREEN
red = Fore.RED
yellow = Fore.YELLOW
blue = Fore.BLUE
reset = Fore.RESET
 
if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_external_in(subdir, script, *args):
    py = shutil.which("python3") or shutil.which("python") or sys.executable
    script_path = os.path.join(BASE_DIR, subdir, script)
    cwd = os.path.dirname(script_path)

    if not os.path.isfile(script_path):
        print(f"\n[!] File tidak ditemukan: {script_path}")
        print("    Cek lagi nama folder & filenya.")
        input("ENTER untuk kembali...")
        return

    cmd = [py, script_path, *map(str, args)]
    rc = subprocess.call(cmd, cwd=cwd)
    if rc != 0:
        input(f"\n[!] Script exit code {rc}. ENTER untuk kembali...")
    
def key_pressed():
    if platform.system() == "Windows":
        if msvcrt.kbhit():
            return msvcrt.getch()
        return None
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            rlist, _, _ = select.select([sys.stdin], [], [], 0)
            if rlist:
                return sys.stdin.read(1).encode()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None


# ====================== MOBAPAY CONFIG ======================
def print_moba_banner_green():
    print(Fore.GREEN + 
    ":::::::::::::::::::::::::::::::::::::::::::::\n" +
    ":'##::::'##::'#######::'########:::::'###::::\n" +
    ": ###::'###:'##.... ##: ##.... ##:::'## ##:::\n" +
    ": ####'####: ##:::: ##: ##:::: ##::'##:. ##::\n" +
    ": ## ### ##: ##:::: ##: ########::'##:::. ##:\n" +
    ": ##. #: ##: ##:::: ##: ##.... ##: #########:\n" +
    ": ##:.:: ##: ##:::: ##: ##:::: ##: ##.... ##:\n" +
    ": ##:::: ##:. #######:: ########:: ##:::: ##:\n" +
    "..::::::..:::.......:::........:::..:::::..::" + Style.RESET_ALL)
    print(Fore.GREEN +
          "::::::::::: MOBAPAY SCRIPT v1.0 :::::::::::::\n" +
          ":::::::: Author: Kings Faza | 2025 ::::::::::\n" +
          ":::: Description: Tool Order & Direk Web ::::\n" +
          ":::::::::::::::::::::::::::::::::::::::::::::\n" +
          Style.RESET_ALL)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_FILE = ".token"
EMAIL_FILE = ".email"

def load_token_mobapay():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            try:
                token_data = json.load(f)
                exp = token_data.get("exp", 0)
                if exp > int(time.time()):
                    return token_data["token"]
                else:
                    print("⚠️ Token expired.")
            except Exception:
                print("⚠️ File token rusak.")
    return save_new_token_mobapay()

def save_new_token_mobapay():
    new_token = input("🔐 Masukkan Token Mobapay: ").strip()
    payload_part = new_token.split(".")[1] + "=="
    try:
        decoded = json.loads(
            base64.urlsafe_b64decode(payload_part.encode("utf-8")).decode("utf-8")
        )
        exp = decoded.get("exp", int(time.time()) + 3600)
    except Exception:
        exp = int(time.time()) + 3600

    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": new_token, "exp": exp}, f)
    print("✅ Token baru disimpan.")
    return new_token


def load_email():
    if os.path.exists(EMAIL_FILE):
        with open(EMAIL_FILE, "r") as f:
            return f.read().strip()
    else:
        return save_new_email()

def save_new_email():
    new_email = input("📧 Masukkan email untuk transaksi: ").strip()
    with open(EMAIL_FILE, "w") as f:
        f.write(new_email)
    print("✅ Email disimpan ke .email")
    return new_email

ALLOWED_DOMAINS = ["sgsnssdk.com"]
running = True

def format_link_display(url):
    if "sgsnssdk.com" in url:
        return url
    elif "global.gold.razer.com" in url:
        return "https://global.gold.razer.com/"
    elif "codapayments.com" in url:
        return "https://airtime.codapayments.com/"
    else:
        return url[:50]

def create_order(user_id, server_id, choice, mode="web"):
    url = "https://api.mobapay.com/pay/order"

    if choice == "1":
        # Weekly Diamond Pass
        payload = {
            "app_id": 100000,
            "game_user_key": user_id,
            "game_server_key": server_id,
            "email": email_user,
            "currency_code": "IDR",
            "country_code": "ID",
            "goods_id": 120991,
            "lang": "en",
            "num": 1,
            "pay_channel_sub_id": 10093,
            "price_pay": 2700000,
            "amount_pay": 2700000,
            "shop_id": 1001,
            "terminal_type": "WAP" if MODE_MOBAPAY == "mobile" else "WEB",
            "network": "android" if MODE_MOBAPAY == "mobile" else "",
            "net": "wifi" if MODE_MOBAPAY == "mobile" else ""
        }

    elif choice == "2":
        # DM 5
        payload = {
            "app_id": 100000,
            "game_user_key": user_id,
            "game_server_key": server_id,
            "email": email_user,
            "currency_code": "IDR",
            "country_code": "ID",
            "goods_id": 48,
            "lang": "en",
            "num": 1,
            "pay_channel_sub_id": 10118,
            "price_pay": 141000,
            "amount_pay": 141000,
            "shop_id": 1001,
            "terminal_type": "WAP" if MODE_MOBAPAY == "mobile" else "WEB",
            "network": "android" if MODE_MOBAPAY == "mobile" else "",
            "net": "wifi" if MODE_MOBAPAY == "mobile" else ""
        }
        
    elif choice == "3":
        # DM 44
        payload = {
            "app_id": 100000,
            "game_user_key": user_id,
            "game_server_key": server_id,
            "email": email_user,
            "currency_code": "IDR",
            "country_code": "ID",
            "goods_id": 52,
            "lang": "en",
            "num": 1,
            "pay_channel_sub_id": 10118,
            "price_pay": 1128000,
            "amount_pay": 1128000,
            "shop_id": 1001,
            "terminal_type": "WAP" if MODE_MOBAPAY == "mobile" else "WEB",
            "network": "android" if MODE_MOBAPAY == "mobile" else "",
            "net": "wifi" if MODE_MOBAPAY == "mobile" else ""
        }

    elif choice == "4":
        # DM 59 ← Tambahan baru
        payload = {
            "app_id": 100000,
            "game_user_key": user_id,
            "game_server_key": server_id,
            "email": email_user,
            "currency_code": "IDR",
            "country_code": "ID",
            "goods_id": 53,
            "lang": "en",
            "num": 1,
            "pay_channel_sub_id": 10118,
            "price_pay": 1504000,
            "amount_pay": 1504000,
            "shop_id": 1001,
            "terminal_type": "WAP" if MODE_MOBAPAY == "mobile" else "WEB",
            "network": "android" if MODE_MOBAPAY == "mobile" else "",
            "net": "wifi" if MODE_MOBAPAY == "mobile" else ""
        }

    else:
        print(Fore.RED + "❌ Pilihan tidak valid.\n" + Style.RESET_ALL)
        return None

    response = requests.post(url, headers=HEADERS_MOBAPAY, json=payload, verify=False)
    try:
        res_json = response.json()
        if response.ok and res_json.get("code") == 0:
            data = res_json["data"]
            server_id = data.get("server_id") or "-"
            print(f"📦 Order ID: {data['order_id']} | Amount: {data['amount_pay']} | User: {data['user_name']} — Cek link...")
            return data["order_id"]
        else:
            print("❌ Gagal membuat order, ulangi...")
    except Exception as e:
        print("❌ Gagal mendapatkan link pembayaran.")
    return None

def is_valid_link(link):
    VALID_DOMAINS_WEB = ["sgsnssdk.com"]
    VALID_DOMAINS_MOBILE = [
        "gopay.co.id/app/merchanttransfer",
        "f-p.sgsnssdk.com"
    ]

    if MODE_MOBAPAY == "mobile":
        return any(domain in link for domain in VALID_DOMAINS_MOBILE)
    else:
        return any(domain in link for domain in VALID_DOMAINS_WEB)
    
def create_payment(order_id):
    url = "https://api.mobapay.com/pay/order/payment"
    payload = {
        "order_id": order_id,
        "return_url": f"https://www.mobapay.com/order?appid=100000&order={order_id}&r=ID",
        "terminal_type": "WAP" if MODE_MOBAPAY == "mobile" else "WEB",
        "network": "android" if MODE_MOBAPAY == "mobile" else "",
        "net": "wifi" if MODE_MOBAPAY == "mobile" else ""
    }

    try:
        response = requests.post(url, headers=HEADERS_MOBAPAY, json=payload, verify=False)

        # MODE MOBILE (Redirect APK)
        if MODE_MOBAPAY == "mobile":
            location = response.headers.get("location", "")
            print(f"📍 Redirect location: {location}")

            # Coba ambil dari header dulu
            gopay_link = extract_gopay_link(location)
            if gopay_link:
                return gopay_link
            else:
                print("🚫 Gagal redirect, cek JSON...")

                try:
                    res_json = response.json()
                    if response.ok and res_json.get("code") == 0:
                        gopay_link = res_json["data"].get("payment_url", "")
                    if gopay_link:
                        if is_valid_link(gopay_link):
                            return gopay_link
                        else:
                            print("❌ Link tidak valid -- lewati...")
                            time.sleep(2)
                    else:
                        print("❌ Gagal parsing data JSON:", res_json)
                except Exception as e:
                    print("❌ Exception parsing JSON:", e)

        # MODE WEB
        else:
            res_json = response.json()
            if response.ok and res_json.get("code") == 0:
                return res_json["data"].get("payment_url", "")
            else:
                print("❌ Gagal dapat link dari mode web:", res_json)

    except Exception as e:
        print("❌ Gagal parsing response payment:", e)

    return None

def extract_gopay_link(location_header):
    try:
        if "link=" in location_header:
            match = re.search(r"link=(https%3A%2F%2Fgopay.co.id%2Fapp%2Fmerchanttransfer[^\"]+)", location_header)
            if match:
                return unquote(match.group(1))
    except:
        pass
    return None

def is_allowed_link(url):
    if MODE_MOBAPAY == "web":
        return "sgsnssdk.com" in url
    elif MODE_MOBAPAY == "mobile":
        return "gopay.co.id/app/merchanttransfer" in url or "f-p.sgsnssdk.com" in url
    return False

def simpan_riwayat(order_id, status, user_id, server_id, nominal, link, mode="web"):
    now = datetime.now()
    tanggal = now.strftime("%Y-%m-%d")
    jam = now.strftime("%H:%M:%S")

    os.makedirs("logs", exist_ok=True)

    # File log RIWAYAT terpisah berdasarkan mode
    log_file = os.path.join("logs", f"riwayat_{mode.upper()}_{tanggal}.txt")

# Tambahkan header jika file belum ada
    if not os.path.exists(log_file):
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"====== LOG ORDERAN MODE {mode.upper()} [{tanggal}] ======\n")

    # ✅ SIMPAN HANYA YANG VALID
    if status == "✅ LINK VALID":
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{jam}] {status} | ORDER_ID: {order_id} | USER: {user_id} | SERVER: {server_id} | NOMINAL: {nominal}\n")

    # Validasi hanya simpan dan buka link jika direct
    parsed_domain = link.split("/")[2] if "://" in link else ""
    non_direct_domains = ["codapayments.com", "razer.com"]

    platform_pc = is_pc()

    if status == "✅ LINK VALID" and not any(nd in parsed_domain for nd in non_direct_domains):
        # Pisahkan file link valid berdasarkan mode
        if mode == "mobile":
            link_log_file = os.path.join("logs", f"link_pay_mobile_{tanggal}.txt")
        else:
            link_log_file = os.path.join("logs", f"link_pay_web_{tanggal}.txt")

        with open(link_log_file, "a", encoding="utf-8") as f:
            f.write(f"[{tanggal} {jam}] {link.strip()}\n")

        # Tampilkan dan buka sesuai platform
        if mode == "mobile":
            if platform_pc:
                print("🌐 Link MOBILE dibuka (PC)")
                buka_link(link)
            else:
                print("💾 Link MOBILE disimpan (tidak dibuka di HP)")
        else:
            print("💾 Link WEB disimpan (PC/HP)")
            buka_link(link)

def pilih_log_untuk_cek_atau_hapus():
    log_folder = "logs"
    os.makedirs(log_folder, exist_ok=True)  # Pastikan folder ada

    log_files = sorted(
        [f for f in os.listdir(log_folder) if f.startswith("riwayat_") and f.endswith(".txt")],
        key=lambda x: os.path.getmtime(os.path.join(log_folder, x))
    )

    if not log_files:
        print("📭 Tidak ada file log harian ditemukan.")
        return None

    print("\n📁 Daftar riwayat harian tersedia :\n")
    for idx, filename in enumerate(log_files, start=1):
        print(f"{idx}. {filename}   🗑️ Hapus: D{idx}")

    pilihan = input("\n📝 Pilih (1-{}) untuk cek atau ketik D1, D2, dst untuk hapus : ".format(len(log_files))).strip().upper()

    if pilihan.startswith("D") and pilihan[1:].isdigit():
        index = int(pilihan[1:]) - 1
        if 0 <= index < len(log_files):
            path_to_delete = os.path.join(log_folder, log_files[index])
            os.remove(path_to_delete)
            print(f"🗑️ File log '{log_files[index]}' berhasil dihapus.")
        else:
            print("❌ Nomor log tidak valid.")
        navigasi_akhir_moba()
        return

    elif pilihan.isdigit():
        index = int(pilihan) - 1
        if 0 <= index < len(log_files):
            return os.path.join(log_folder, log_files[index])
        else:
            print("❌ Nomor log tidak valid.")
            return
    else:
        print("❌ Input tidak dikenali.")
        return
        
def bersihkan_warna(teks):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', teks)
            
def proses_cek_order_dan_simpan(path_log):
    try:
        with open(path_log, encoding="utf-8") as f:
            baris_log = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + f"❌ File log tidak ditemukan: {path_log}")
        navigasi_akhir_moba()  # ← auto balik
        return

    log_list = []
    for baris in baris_log:
        if "✅ LINK VALID" in baris:
            parts = baris.strip().split("|")
            log_dict = {}
            for part in parts:
                if ":" in part:
                    key, val = part.strip().split(":", 1)
                    log_dict[key.strip()] = val.strip()
            if "ORDER_ID" in log_dict and "USER" in log_dict and "SERVER" in log_dict:
                log_list.append((
                    log_dict["ORDER_ID"],
                    log_dict["USER"],
                    log_dict["SERVER"]
                ))

    if not log_list:
        print(Fore.RED + "❌ Tidak ada ORDER_ID valid ditemukan dalam log.")
        navigasi_akhir_moba()
        return

    print(f"\n🔎 Mengecek status {len(log_list)} ORDER_ID...\n")

    hasil_status = []
    tanggal = datetime.now().strftime("%Y-%m-%d")
    hasil_file = f"logs/status_order_{tanggal}.txt"

    try:
        for order_id, user_id, server_id in log_list:
            key = key_pressed()
            if key in [b'\r', b'\n']:
                print(Fore.YELLOW + "\n🔁 Pengecekan dihentikan oleh user. Kembali ke menu...")
                break

            try:
                status = cek_status_order(order_id, user_id, server_id)
                print(f"📄 ORDER_ID: {order_id} ➜ {status}")
                hasil_status.append(f"{order_id} ➜ {bersihkan_warna(status)}")
            except Exception as e:
                print(Fore.RED + f"❌ Gagal cek status ORDER_ID {order_id}: {type(e).__name__}")
                hasil_status.append(f"{order_id} ➜ ERROR: {type(e).__name__}")
                continue

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n🔁 Pengecekan dibatalkan oleh user (CTRL+C).")

    except Exception as e:
        print(Fore.RED + f"\n🚨 Terjadi kesalahan fatal saat cek order: {type(e).__name__}")
        navigasi_akhir_moba()
        return

    with open(hasil_file, "a", encoding="utf-8") as f:
        f.write("\n".join(hasil_status) + "\n")

    print(Fore.CYAN + f"📁 Hasil status disimpan di: {hasil_file}")

import platform
import os

def is_android():
    return any(key in os.environ for key in ["ANDROID_ROOT", "ANDROID_DATA", "BOOTCLASSPATH"])

def is_pc():
    return not is_android()

def buka_link(link):
    try:
        pyperclip.copy(link)
        print("📋 Link disalin ke clipboard!")
    except pyperclip.PyperclipException:
        print("⚠️ Gagal menyalin link (clipboard tidak tersedia).")

    print("🌐 Link dibuka sesuai platform...")

    try:
        if platform.system() == "Windows":
            os.startfile(link)  # Buka default browser di Windows
        elif is_pc():
            subprocess.run(["xdg-open", link], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif is_android():
            subprocess.run(["am", "start", "-a", "android.intent.action.VIEW", "-d", link],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            print("❌ Platform tidak dikenal, link tidak bisa dibuka otomatis.")
    except Exception as e:
        print(f"❌ Gagal membuka link otomatis: {e}")

def auto_cek_semua_orderan():
    path_log = pilih_log_untuk_cek_atau_hapus()
    if not path_log:
        return
    proses_cek_order_dan_simpan(path_log)
    
def order_mobapay():
    global MODE_MOBAPAY
    print("\n🎮 PILIH MODE :")
    print("1. Website (Default)")
    print("2. Mobile (Direk APK)")
    mode_input = input("\nPilih mode (1/2): ").strip()
    MODE_MOBAPAY = "mobile" if mode_input == "2" else "web"
    print(Fore.CYAN + f"\n🔧 Mode aktif: {'MOBILE (APK)' if MODE_MOBAPAY == 'mobile' else 'WEB'}" + Style.RESET_ALL)
    
    # Lanjut proses input user ID, nominal, dll
    
    # ==== PARSING MULTI USER DAN TARGET ====
    
    input_ids = input("\n📥 Masukkan User ID & Server ID (dipisah koma): ").strip()
    input_targets = input("🎯 Target link valid masing-masing ID (dipisah koma): ").strip()
    
    id_list = [x.strip() for x in input_ids.split(",") if x.strip()]
    target_list = [int(x.strip()) for x in input_targets.split(",") if x.strip()]
    
    targets = []
    format_salah = False
    for i, id_pair in enumerate(id_list):
        parts = id_pair.strip().split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            print(Fore.RED + f"❌ Format salah pada pasangan ke-{i+1}: '{id_pair}'. Gunakan format: UserID ServerID" + Style.RESET_ALL)
            format_salah = True
            break
        user_id, server_id = parts
        target = target_list[i] if i < len(target_list) else 1
        targets.append({
            "user_id": user_id,
            "server_id": server_id,
            "target": target
        })
        if format_salah:
            continue
        else:
            continue
        
    print(Fore.CYAN + "\n❄  Pilih Nominal:")
    print(Fore.CYAN + "   1. 💎 Weekly Diamond Pass")
    print(Fore.CYAN + "   2. 💎 Diamond 5")
    print(Fore.CYAN + "   3. 💎 Diamond 44")
    print(Fore.CYAN + "   4. 💎 Diamond 59")
    choice = input(Fore.CYAN + "❄  Pilih (1/2/3): " + Style.RESET_ALL).strip()
    
    if choice == "1":
        nominal_label = "Weekly Diamond Pass"
    elif choice == "2":
        nominal_label = "DM 5"
    elif choice == "3":
        nominal_label = "DM 44"
    elif choice == "4":
        nominal_label = "DM 59"
    else:
        print(Fore.RED + "❌ Pilihan tidak valid. ")
        return
    valid_count = 0
    attempt = 0
    
    # ==== LOOP FARMING PER ID DENGAN TARGET MASING-MASING ====
    for target in targets:
        user_id = target["user_id"]
        server_id = target["server_id"]
        target_valid = target["target"]
        valid_count = 0
        attempt = 1
        dibatalkan_manual = False
    
        while valid_count < target_valid:
            key = key_pressed()
            if key in [b'\r', b'\n']:
                dibatalkan_manual = True
                print(Fore.RED + f"\n❌ Dibatalkan manual. Total link valid didapat: {valid_count}" + Style.RESET_ALL)
                break
    
            try:
                print(f"\n🛠️ [Percobaan ke-{attempt}] Membuat order...")
    
                while True:
                    try:
                        order_id = create_order(user_id, server_id, choice)
                        break
                    except (requests.exceptions.RequestException, socket.error):
                        tunggu_koneksi()
                        continue
                
                if not order_id:
                    attempt += 1
                    continue
    
                payment_url = create_payment(order_id)
                if not payment_url:
                    attempt += 1
                    continue
    
                if is_allowed_link(payment_url):
                    valid_count += 1
                    print(f"✅ Link Valid ke-{valid_count} : {format_link_display(payment_url)}\n")
                    status = "✅ LINK VALID"
                    simpan_riwayat(order_id, status, user_id, server_id, nominal_label, payment_url, mode=MODE_MOBAPAY)
                else:
                    domain = urlparse(payment_url).netloc
                    print(f"❌ Link tidak valid [{domain}] -- lewati...")
                    status = "❌ LINK TIDAK VALID"
                    simpan_riwayat(order_id, status, user_id, server_id, nominal_label, payment_url, mode=MODE_MOBAPAY)
    
                    attempt += 1
                time.sleep(2.5)
    
            except Exception as e:
                error_msg = str(e)
            
                if "Failed to establish a new connection" in error_msg or "No address associated" in error_msg:
                    print(Fore.RED + "🔺 Gagal konek ke server Mobapay (periksa koneksi)")
                elif "RemoteDisconnected" in error_msg:
                    print(Fore.RED + "🔺 Koneksi ditutup oleh server (RemoteDisconnected)")
                elif "Connection aborted" in error_msg:
                    print(Fore.RED + "🔺 Koneksi gagal / abort oleh server")
                else:
                    print(Fore.RED + f"🔺 Terjadi error: {error_msg}")
                break

        if not dibatalkan_manual:
            print(Fore.GREEN + f"🎯 Selesai! {valid_count} link valid berhasil didapatkan.\n" + Style.RESET_ALL)
            
        
def navigasi_akhir_moba():
    while True:
        pilihan = input("\nPilih / Back [b]: ").strip().lower()
        if pilihan == "1":
            order_mobapay()
            continue
        elif pilihan == "2":
            tampilkan_order_valid_dari_log()
            continue
        elif pilihan == "3":
            auto_cek_semua_orderan()
            continue
        elif pilihan == "b":
            return "exit"
        else:
            print(Fore.RED + "❌ Pilihan tidak valid.")
            
def menu_moba():
    global email_user
    global HEADERS_MOBAPAY
    global MODE_MOBAPAY
   
    X_TOKEN = load_token_mobapay()
    email_user = load_email()
    
    HEADERS_MOBAPAY = {
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "https://www.mobapay.com",
        "Referer": "https://www.mobapay.com/",
        "User-Agent": "Mozilla/5.0",
        "X-Lang": "en",
        "X-Token": X_TOKEN,
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-platform": '"Windows"',
        "sec-ch-ua-mobile": "?0",
    }

    while True:
        print_moba_banner_green()
        print(Fore.CYAN + "1. 🔁 Order Automatis")
        print(Fore.CYAN + "2. 📄 Tampilkan Orderan Valid hari ini")
        print(Fore.CYAN + "3. 📦 Auto-cek semua Orderan & Simpan")

        pilih = input(Fore.YELLOW + "\nPilih / Back [b]: " + Style.RESET_ALL).strip()

        if pilih == "1":
            MODE_MOBAPAY = None
            order_mobapay()
        
        elif pilih == "2":
            tampilkan_order_valid_dari_log()

        elif pilih == "3":
            auto_cek_semua_orderan()

        elif pilih.lower() == "b":
            break
        else:
            print(Fore.RED + "❌ Pilihan tidak valid.")

        hasil_navigasi = navigasi_akhir_moba()
        if hasil_navigasi == "exit":
            break

def format_rupiah(angka):
    try:
        angka = int(angka)
        return f"{angka:,}".replace(",", ".")
    except:
        return angka

def cek_status_order(order_id, user_id, server_id):
    url = f"https://api.mobapay.com/pay/order?game_user_key={user_id}&game_server_key={server_id}&order_id={order_id}"

    try:
        response = requests.get(url, headers=HEADERS_MOBAPAY, verify=False)
        res = response.json()
    except json.JSONDecodeError as e:
        print(Fore.RED + f"❌ Error parsing: {e}" + Style.RESET_ALL)
        print(Fore.LIGHTBLACK_EX + f"🔎 Response mentah: {response.text}" + Style.RESET_ALL)
        return

    if res.get("code") == 0:
        data = res["data"]

        order_id = data.get("order_id")
        username = data.get("username", "-")
        email = data.get("email", "-")
        # nominal = format_rupiah(data.get("price_pay", 0))  # Harga awal
        amount = format_rupiah(data.get("amount_pay", 0))  # Harga setelah diskon
        metode = data.get("pay_channel_sub_name", "-")
        waktu_raw = data.get("create_time", "-")
        item = data.get("goods_name", "-")
        game_id = data.get("user_name", "-")

        try:
            waktu = datetime.fromtimestamp(int(waktu_raw), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S (UTC)")
        except:
            waktu = waktu_raw
        
        print(Fore.YELLOW + "📦 [Status Order]")
        print(f"🆔 Order No.    : {order_id}")
        print(f"🕒 Payment Time : {waktu}")
        print(f"🎮 Game ID      : {user_id}({server_id})")
        print(f"👤 Username     : {username}")
        print(f"📧 Email        : {email}")
        # print(f"💵 Price            : {nominal} Rp.")
        print(f"💰 Amount       : {amount} Rp.")
        print(f"💳 Payment      : {metode}")
        print(f"📦 Item Name    : {item}")

        status_code = data.get('status')
        status_str = (
            Fore.GREEN + "✅ Status       : SUDAH DIBAYAR\n" + Style.RESET_ALL if status_code == 4 else
            Fore.YELLOW + "⏳ Status       : BELUM DIBAYAR\n" + Style.RESET_ALL if status_code == 2 else
            Fore.RED + f"❌ Status       : XPIRED\n" + Style.RESET_ALL if status_code == 6 else
            Fore.RED + f"❌ Status       : TIDAK DIKETAHUI\n ({status_code})" + Style.RESET_ALL
        )
        print(status_str)
        return status_str.strip()

    else:
        print(Fore.RED + "❌ Gagal mendapatkan detail order.\n" + Style.RESET_ALL)
        return "GAGAL"
        
def tampilkan_order_valid_dari_log(tanggal=None):
    if tanggal is None:
        tanggal = datetime.now().strftime("%Y-%m-%d")

    log_paths = [
        os.path.join("logs", f"riwayat_WEB_{tanggal}.txt"),
        os.path.join("logs", f"riwayat_MOBILE_{tanggal}.txt")
    ]

    found = False
    for log_path in log_paths:
        if not os.path.exists(log_path):
            continue

        print(Fore.CYAN + f"\n📄 Menampilkan ORDER_ID link valid di: {log_path}" + Style.RESET_ALL)
        with open(log_path, "r", encoding="utf-8") as file:
            for line in file:
                if "✅ LINK VALID" in line:
                    parts = line.strip().split(" | ")
                    data = {}
                    for part in parts:
                        if ": " in part:
                            k, v = part.strip().split(": ", 1)
                            data[k.strip()] = v.strip()
                    
                    print(
                        f"\n✅ ORDER_ID: {data.get('ORDER_ID', '-')}"
                        f" | {Fore.BLUE}👤 USER: {data.get('USER', '-')}{Style.RESET_ALL}"
                        f" | 📄 SERVER: {data.get('SERVER', '-')}"
                        f" | 💎 NOMINAL: {data.get('NOMINAL', '-')}"
                    )
                    found = True
    
    if not found:
        print(Fore.RED + "❌ Tidak ada link valid ditemukan di log hari ini." + Style.RESET_ALL)
                    
def cek_semua_order_valid_dari_log(tanggal=None):
    if tanggal is None:
        tanggal = datetime.now().strftime("%Y-%m-%d")

    log_path = os.path.join("logs", f"riwayat_{tanggal}.txt")
    export_path = os.path.join("logs", f"status_order_{tanggal}.txt")

    if not os.path.exists(log_path):
        print(f"❌ File log tidak ditemukan: {log_path}")
        return

    print(Fore.CYAN + f"\n📄 Mengecek semua ORDER_ID VALID dari: {log_path}" + Style.RESET_ALL)

    with open(log_path, "r", encoding="utf-8") as file, open(export_path, "w", encoding="utf-8") as export:
        export.write(f"==== STATUS ORDER dari LOG: {tanggal} ====\n")

        for line in file:
            if "✅ LINK VALID" in line:
                parts = line.strip().split("|")

                # Parsing semua bagian log jadi dict
                log_dict = {}
                for part in parts:
                    if ":" in part:
                        key, val = part.strip().split(":", 1)
                        log_dict[key.strip()] = val.strip()

                order_id = log_dict.get("ORDER_ID", "")
                user_id = log_dict.get("USER", "")
                server_id = log_dict.get("SERVER", "")
                nominal = log_dict.get("NOMINAL", "")

                if order_id and user_id and server_id:
                    url = f"https://api.mobapay.com/pay/order?game_user_key={user_id}&game_server_key={server_id}&order_id={order_id}"
                    response = requests.get(url, headers=HEADERS_MOBAPAY, verify=False)
                    try:
                        res = response.json()
                        if res.get("code") == 0:
                            data = res["data"]
                            status_code = data.get('order_status')
                            status_str = (
                                "✅ SUDAH DIBAYAR" if status_code == 2 else
                                "⏳ BELUM DIBAYAR" if status_code == 1 else
                                "❌ KADALUARSA" if status_code == 5 else
                                "❌  XPIRED" if status_code == 6 else
                                f"❓ STATUS {status_code}"
                            )
                            hasil = f"[{order_id}] {status_str} | USER: {user_id} | SERVER: {server_id} | NOMINAL: {nominal}"
                            print(hasil)
                            export.write(hasil + "\n")
                        else:
                            print(f"[{order_id}] ❌ Gagal ambil status")
                            export.write(f"[{order_id}] ❌ Gagal ambil status\n")
                    except Exception as e:
                        print(f"[{order_id}] ❌ Error: {e}")
                        export.write(f"[{order_id}] ❌ Error: {e}\n")

                    time.sleep(1.5)

    print(Fore.GREEN + f"✅ Semua status selesai dicek dan disimpan ke: {export_path}\n" + Style.RESET_ALL)
    
# ====================== OTP CONFIG FIX ======================
def print_otp_ascii():
    print(Fore.GREEN + '''
8   8 8   8 8""""8        8"""88 ""8"" 8""""8
8   8 8   8 8    8        8    8   8   8    8
8eee8 8e  8 8eeee8ee      8    8   8e  8eeee8
88  8 88  8 88     8 eeee 8    8   88  88
88  8 88  8 88     8      8    8   88  88
88  8 88ee8 88eeeee8      8eeee8   88  88
''' + Style.RESET_ALL)

def load_api_key_otp():
    path = ".keys"
    if not os.path.exists(path):
        print(f"{Fore.RED}[!] File {path} tidak ditemukan.")
        return None
    with open(path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        print(f"{Fore.RED}[!] File {path} kosong.")
        return None
    return lines[0]  # ambil baris pertama saja
    
def check_balance(api_key):
    balance_url = f'https://hero-sms.com/stubs/handler_api.php?api_key={api_key}&action=getBalance'
    response = requests.get(balance_url)
    if response.status_code == 200:
        try:
            balance_data = response.text.strip().split(':')
            if len(balance_data) == 2 and balance_data[0] == 'ACCESS_BALANCE':
                balance = float(balance_data[1])
                return balance
            else:
                print(f'Error: Respons tidak valid. Data saldo tidak ditemukan.')
                return None
        except ValueError:
            print(f'Error: Gagal mendapatkan saldo. Respons tidak valid.')
            return None
    else:
        print(f"{Fore.RED}Gagal ambil saldo. Status code: {response.status_code}")
        return None

def check_number_status(api_key, number_id):
    status_url = f'https://hero-sms.com/stubs/handler_api.php?api_key={api_key}&action=getStatus&id={number_id}'
    response = requests.get(status_url)
    return response.text.strip()

def beli_nomor(api_key, service, operator, country='6', max_retry=3, retry_delay=5):
    url = f'https://hero-sms.com/stubs/handler_api.php?api_key={api_key}&action=getNumber&service={service}&operator={operator}&country={country}'
    
    for attempt in range(1, max_retry + 1):
        try:
            response = requests.get(url, timeout=10).text.strip()

            if "ACCESS_NUMBER" in response:
                _, number_id, number = response.split(':')
                return number_id, number
            else:
                print(Fore.RED + f"Gagal mendapatkan nomor: {response}")
                return None, None

        except requests.exceptions.RequestException:
            print(Fore.YELLOW + f"⚠️  Koneksi error ({attempt}/{max_retry}) - mencoba lagi dalam {retry_delay} detik...")
            time.sleep(retry_delay)

    print(Fore.RED + "❌ Gagal beli nomor setelah beberapa percobaan.\n")
    return None, None

def pilih_service():
    print_otp_ascii()
    
    layanan_text = "LAYANAN OTP"
    rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.LIGHTRED_EX]
    rainbow_title = "".join([rainbow_colors[i % len(rainbow_colors)] + c for i, c in enumerate(layanan_text)]) + Style.RESET_ALL
    print(rainbow_title + " :\n")

    layanan = [
        "1. Gojek",
        "2. Blibli",
        "3. Dana",
        "4. Gmail",
        "5. Lazada",
        "6. Tokopedia",
        "7. Qpon",
        "8. Other"
    ]

    for item in layanan:
        print(item)

    mapping = {
        '1': 'ni',
        '2': 'fk',
        '3': 'fr',
        '4': 'go',
        '5': 'dl',
        '6': 'xd',
        '7': 'bnu',
        '8': 'ot'
    }

    while True:
        pilihan = input(Fore.YELLOW + "\nPilih / Back [b] : " + Style.RESET_ALL).strip().lower()

        if pilihan == "":
            print(Fore.RED + "Tidak ada pilihan. Ulangi..." + Style.RESET_ALL)
            continue

        if pilihan == "b":
            print(Fore.RED + "Kembali ke menu utama." + Style.RESET_ALL)
            return None

        if pilihan in mapping:
            return mapping[pilihan]

        print(Fore.RED + "Pilihan tidak valid. Ulangi..." + Style.RESET_ALL)

def load_opsel_otp():
    operator_text = "\nOPERATOR"
    rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.LIGHTRED_EX]
    rainbow_title = "".join([rainbow_colors[i % len(rainbow_colors)] + c for i, c in enumerate(operator_text)]) + Style.RESET_ALL
    print(rainbow_title + " :\n")

    print("1. Axis       2. Telkomsel   3. Indosat")
    print("4. Three      5. Smartfren   6. Acak")

    mapping = {
        '1': 'axis',
        '2': 'telkomsel',
        '3': 'indosat',
        '4': 'tri',
        '5': 'smartfren',
        '6': 'ANY'
    }

    while True:
        pilihan = input(Fore.YELLOW + "\nPilih / Back [b] : " + Style.RESET_ALL).strip().lower()
        if pilihan == "":
            print(Fore.RED + "Operator tidak valid. ulangi..." + Style.RESET_ALL)
            continue
        if pilihan == "b":
            return "b"
        if pilihan in mapping:
            return mapping[pilihan]
        print(Fore.RED + "Pilihan tidak valid. ulangi..." + Style.RESET_ALL)


def get_operator_nama(operator_id):
    mapping = {
        '1': 'Axis',
        '2': 'Telkomsel',
        '3': 'Indosat',
        '4': 'Tri',
        '5': 'Smartfren',
        '6': 'Acak'
    }
    return mapping.get(str(operator_id), operator_id)
    
def tunggu_koneksi(pesan_khusus=""):
    print(f"{Fore.RED}📡 Koneksi terputus. Menunggu koneksi kembali...")
    while True:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            print(f"{Fore.YELLOW}✅ Koneksi aman Kembali boss...")
            time.sleep(2)
            if pesan_khusus:
                print(f"{Fore.CYAN}{pesan_khusus}")
            return
        except OSError:
            time.sleep(3)
            
import re

def extract_otp(text: str):
    # Cari angka 4–8 digit; utamakan yang dekat kata "OTP/kode/code"
    near = re.search(r'(?i)(otp|kode|code)\D{0,10}(\d{4,8})', text)
    if near:
        return near.group(2)
    # fallback: ambil grup angka 4–8 digit terakhir (hindari nempel angka lain)
    all_nums = re.findall(r'(?<!\d)\d{4,8}(?!\d)', text)
    return all_nums[-1] if all_nums else None

def ask_int(prompt, default):
    s = input(f"{prompt} [{default}]: ").strip()
    return int(s) if s.isdigit() else default

def daftar_otp():
    api_key = load_api_key_otp()
    if not api_key:
        print(Fore.RED + "Gagal memuat API Key dari .keys")
        return

    balance_rub = check_balance(api_key)
    rub_to_idr_exchange_rate = 156
    balance_idr = round(balance_rub * rub_to_idr_exchange_rate)
    MIN_RUB = 0.05

    if balance_rub is None:
        print(Fore.RED + "Gagal mengambil saldo.")
        return

    if balance_rub < MIN_RUB:
        print(Fore.RED + f"Saldo Anda ${balance_rub:.4f} terlalu rendah. Minimum 0.05 Rub dibutuhkan.")
        print(Fore.LIGHTBLACK_EX + "[SILAKAN ISI SALDO DI HEROSMS DAN COBA LAGI]\n")
        return

    print(f"\n{rainbow_info()} {Fore.GREEN}Saldo HEROSMS anda : ${balance_rub:,.2f} | Rp.{balance_idr}{Style.RESET_ALL}")
    
    service_id = pilih_service()
    if service_id is None:
        return

    loop_operator(api_key, service_id, balance_rub, balance_idr)
    
# === helper untuk buang ENTER yang nyangkut dari input sebelumnya ===
def flush_keys():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, select
        while select.select([sys.stdin], [], [], 0)[0]:
            sys.stdin.readline()


def proses_beli_otp(api_key, service_id, operator, balance_rub, balance_idr):
    country_code = '6'
    country_mapping = {'6': 'Indonesia', '151': 'Chille'}
    country_name = country_mapping.get(country_code, 'Unknown')

    print("\n-------------------------------------")
    otp_services = {
        'ni': 'OTP GOJEK',
        'fk': 'OTP BLIBLI',
        'fr': 'OTP DANA',
        'go': 'OTP GMAIL',
        'dl': 'OTP LAZADA',
        'xd': 'OTP TOKOPEDIA',
        'ot': 'OTP OTHER'
    }
    otp_label = otp_services.get(service_id, f'OTP {service_id.upper()}')
    print(f"\nHEROSMS OTP | {otp_label}")
    print(f"Saldo HEROSMS: {Fore.YELLOW}{balance_rub or 0} Rub | Rp.{balance_idr}")
    print(Fore.LIGHTBLACK_EX + "[Tekan ENTER untuk Batal / Kembali]\n")

    # Target & batas percobaan sesi ini
    target_sukses = ask_int("Target OTP sukses", 1)
    batas_percobaan = ask_int("Batas percobaan (0=tak dibatasi)", 0)
    sukses_count = 0
    percobaan_count = 0

    # ====== LOOP PER NOMOR ======
    while True:
        if target_sukses and sukses_count >= target_sukses:
            input("\n[ENTER] Target OTP sukses terpenuhi → kembali ke menu operator...")
            return
        if batas_percobaan and percobaan_count >= batas_percobaan:
            input("\n[ENTER] Batas percobaan tercapai → kembali ke menu operator...")
            return

        percobaan_count += 1
        print(f"\n--- Order ke-{percobaan_count} (Sukses: {sukses_count}/{target_sukses}) ---")

        # Window singkat: boleh batalkan seluruh sesi sebelum beli nomor
        start_time = time.time()
        while time.time() - start_time < 1.5:
            key = key_pressed()
            if key in [b'\r', b'\n']:
                print(Fore.RED + "\nDibatalkan oleh pengguna. Kembali ke menu operator.")
                return

        # Beli nomor
        try:
            number_id, number = beli_nomor(api_key, service_id, operator, country='6')
        except Exception as e:
            print(Fore.RED + f"\n⚠️  Gagal beli nomor: {e}")
            continue

        if not number_id:
            continue

        # Header nomor aktif
        print(f'Country  : {country_name}')
        print(f'Operator : {get_operator_nama(operator)}')
        print(f'Services : {service_id}')
        print(f'Nomor HP : {Fore.YELLOW}{number}{Style.RESET_ALL}')

        flush_keys()  # buang sisa ENTER

        # ====== POLLING OTP UNTUK NOMOR INI ======
        previous_status = ""
        otp_count_on_this_number = 0   # berapa kali OK pada nomor ini
        ended_by_enter = False         # penanda keluar karena ENTER

        while True:
            try:
                status = check_number_status(api_key, number_id)

                if 'STATUS_OK' in status:
                    raw_msg = status.split(':', 1)[-1].strip()
                    otp_only = extract_otp(raw_msg)

                    if otp_only:
                        print(f"OTP      : {Fore.GREEN}{otp_only}{Style.RESET_ALL}")
                    else:
                        print("OTP      : Tidak ditemukan (bukan format 4–8 digit)")

                    # hitung sukses
                    otp_count_on_this_number += 1
                    # AUTO-RESEND → tetap tunggu OTP berikutnya (tidak break)
                    resend_url = (
                        f"https://hero-sms.com/stubs/handler_api.php?api_key={api_key}"
                        f"&action=setStatus&status=3&id={number_id}"
                    )
                    requests.get(resend_url)
                    print("OTP      : " + Fore.YELLOW + "SUCCESS_RESEND" + Style.RESET_ALL)
                    previous_status = ""

                elif 'STATUS_CANCEL' in status:
                    print(Fore.RED + 'OTP Dibatalkan oleh sistem.' + Style.RESET_ALL)
                    # Jangan kirim status apapun ke SMSHub
                    break  # selesai nomor ini

                else:
                    # Cetak perubahan status (mis. STATUS_WAIT_CODE)
                    if status != previous_status:
                        print(f'OTP      : {status}')
                        previous_status = status

                # Tekan ENTER → DONE jika pernah OK, else CANCEL
                key = key_pressed()
                if key in [b'\r', b'\n']:
                    ended_by_enter = True
                    try:
                        if otp_count_on_this_number > 0:
                            done_url = (
                                f"https://hero-sms.com/stubs/handler_api.php?api_key={api_key}"
                                f"&action=setStatus&status=6&id={number_id}"
                            )
                            requests.get(done_url)
                            print("OTP      : " + Fore.CYAN + "DONE" + Style.RESET_ALL)
                            sukses_count += 1
                        else:
                            cancel_url = (
                                f"https://hero-sms.com/stubs/handler_api.php?api_key={api_key}"
                                f"&action=setStatus&status=8&id={number_id}"
                            )
                            requests.get(cancel_url)
                            print("OTP      : " + Fore.RED + "Nomor dibatalkan" + Style.RESET_ALL)
                    except Exception:
                        pass
                    break  # keluar polling nomor → lanjut evaluasi

                time.sleep(1)

            except requests.exceptions.RequestException:
                tunggu_koneksi("🔁 Melanjutkan polling status OTP...")

        # ====== SELESAI 1 NOMOR → DECISION LANJUT / BALIK ======
        if ended_by_enter and target_sukses and sukses_count >= target_sukses:
            # Kamu menekan ENTER dan target sudah cukup → balik ke operator
            input("\n[ENTER] Target terpenuhi → kembali ke operator...")
            return
        else:
            # Sistem CANCEL atau kamu ENTER tetapi target belum tercapai
            lanjut = input("[ENTER] lanjut... / [b] kembali ke operator: ").strip().lower()
            if lanjut == 'b':
                return
            # ENTER → loop lanjut beli nomor berikutnya

                    
def loop_operator(api_key, service_id, balance_rub, balance_idr):
    while True:
        operator = load_opsel_otp()
        if operator.lower() == "b":
            print(Fore.RED + "Kembali ke menu utama..." + Style.RESET_ALL)
            return
        proses_beli_otp(api_key, service_id, operator, balance_rub, balance_idr)
        hasil = beli_nomor(api_key, service_id, operator)
        if hasil == "batal":
            continue  # ulang pilih operator
        elif hasil == "selesai":
            continue  # ulang pilih operator juga
        
# =============== FARMING FEATURE ===================

def rainbow_info():
        return (Fore.RED + "[" + Fore.YELLOW + "I" + Fore.GREEN + "N" + Fore.CYAN + "F" + Fore.MAGENTA + "O" + Fore.RED + "]" + Fore.RESET)

def rainbow_error():
        return (Fore.RED + "[" + Fore.YELLOW + "E" + Fore.GREEN + "R" + Fore.CYAN + "O" + Fore.MAGENTA + "R" + Fore.RED + "]" + Fore.RESET)

def rainbow_otp():
        return (Fore.RED + "[" + Fore.YELLOW + "O" + Fore.GREEN + "T" + Fore.CYAN + "P" + Fore.MAGENTA + ":" + Fore.RED + "]" + Fore.RESET)

def rainbow_auto():
    return (Fore.RED + "[" + Fore.YELLOW + "A" + Fore.GREEN + "U" + Fore.CYAN + "T" + Fore.MAGENTA + "O" + Fore.RED + "]" + Fore.RESET)

def rainbow_warn():
        return (Fore.RED + "[" + Fore.YELLOW + "W" + Fore.GREEN + "A" + Fore.CYAN + "R" + Fore.MAGENTA + "N" + Fore.RED + "]" + Fore.RESET)
        
def print_farming_ascii():
    print(Fore.GREEN  + "\n███████  " + Fore.YELLOW + "█████  " + Fore.CYAN   + "███████  " + Fore.RED    + "███  ███")
    print(Fore.GREEN  + "██      " + Fore.YELLOW + "██   ██ " + Fore.CYAN   + "██   ██ " + Fore.RED    + "████  ████")
    print(Fore.GREEN  + "█████   " + Fore.YELLOW + "███████ " + Fore.CYAN   + "██████  " + Fore.RED    + "██ ████ ██")
    print(Fore.GREEN  + "██      " + Fore.YELLOW + "██   ██ " + Fore.CYAN   + "██   ██ " + Fore.RED    + "██  ██  ██")
    print(Fore.GREEN  + "██      " + Fore.YELLOW + "██   ██ " + Fore.CYAN   + "██   ██ " + Fore.RED    + "██      ██" + Fore.RESET)
    print(Fore.GREEN + "----------------------------------" + Style.RESET_ALL)
    print(Fore.YELLOW + "   Author: Kings Faza | 2025   " + Style.RESET_ALL)
    print(Fore.CYAN + "  Description: SmsHUB x MitraBL  " + Style.RESET_ALL)
    print(Fore.RED + "----------------------------------" + Style.RESET_ALL)

key_index = 0
API_KEYS = []
API_INDEX = 1

def load_keys(file_path=".keys"):
    try:
        with open(file_path, "r") as f:
            keys = [line.strip() for line in f if line.strip()]
        if not keys:
            raise ValueError("File .keys kosong.")
        return keys
    except FileNotFoundError:
        print(Fore.RED + "File .keys tidak ditemukan.")
        return []
       
def load_all_apikeys():
    global API_KEYS
    if not os.path.exists(".keys"):
        print("❌ File .keys tidak ditemukan.")
        return []
    with open(".keys") as f:
        API_KEYS = [line.strip() for line in f if line.strip()]
    if not API_KEYS:
        print("❌ Tidak ada API key di .keys")
    return API_KEYS

def get_next_key():
    global API_INDEX
    if not API_KEYS:
        load_all_apikeys()
    if len(API_KEYS) == 1:
        return API_KEYS[0]
    key = API_KEYS[API_INDEX % len(API_KEYS)]
    API_INDEX += 1
    return key

def pilih_apikey_interaktif(path=".keys"):
    if not os.path.exists(path):
        print("❌ File .keys tidak ditemukan.")
        return None

    with open(path, "r") as f:
        keys = [line.strip() for line in f if line.strip()]

    if not keys:
        print("❌ Tidak ada API key di .keys")
        return None

    print("\n🔐 PILIH API KEY UNTUK FARMING:\n")
    for i, key in enumerate(keys, start=1):
        print(f"{i}. {key[:6]}****{key[-4:]}")

    while True:
        pilih = input("\nPilih API key (1/2/3) atau [b] kembali: ").strip().lower()
        if pilih == "b":
            return None
        if pilih.isdigit():
            idx = int(pilih) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        print("❌ Pilihan tidak valid.")

def farm_tool():
    import colorama
    colorama.init(autoreset=True)
    from colorama import Fore, Style
    import time

    # ================= PILIH API KEY =================
    api_key = pilih_apikey_interaktif()
    if not api_key:
        print(Fore.RED + "❌ Farming dibatalkan." + Style.RESET_ALL)
        return

    # ================= CEK SALDO =================
    balance_rub = check_balance(api_key)
    rub_to_idr_exchange_rate = 156
    balance_idr = round(balance_rub * rub_to_idr_exchange_rate)
    MIN_RUB = 0.05

    if balance_rub is None:
        print(Fore.RED + "❌ Gagal mengambil saldo." + Style.RESET_ALL)
        return

    if balance_rub < MIN_RUB:
        print(Fore.RED + f"❌ Saldo terlalu rendah: {balance_rub} RUB")
        return

    print(
        f"\n{rainbow_info()} {Fore.GREEN}"
        f"APIKEY AKTIF | Saldo: {balance_rub:.2f} RUB | Rp.{balance_idr}"
        f"{Style.RESET_ALL}"
    )

    # ================= PILIH OPERATOR =================
    print_farming_ascii()
    operator = load_operator_farm()
    if not operator:
        print(Fore.RED + "❌ Farming dibatalkan." + Style.RESET_ALL)
        return

    print(Style.BRIGHT + Fore.MAGENTA + "\n🚀 FARMING DIMULAI...\n" + Style.RESET_ALL)

    # ================= JALANKAN FARMING =================
    mitra_key = "WA-CHECKER"  # placeholder
    jalankan_farming(api_key, mitra_key, operator)

    # ================= NAVIGASI AKHIR =================
    navigasi_akhir_farming()
       
def load_operator_farm():
    rainbow = [
        Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA
    ]
    
    teks = "PILIH OPERATOR :\n"
    print()
    for i, char in enumerate(teks):
        warna = rainbow[i % len(rainbow)]
        print(warna + char, end='')
    print(Style.RESET_ALL)

    print(Fore.WHITE + "1. Axis     2. Telkomsel   3. Indosat")
    print("4. Three    5. Smartfren   6. Acak" + Style.RESET_ALL)

    while True:
        pilihan = input(Fore.YELLOW + "\nPilih / Back [b]: " + Style.RESET_ALL).strip().lower()
        
        if pilihan == "b":
            return None
        
        if not pilihan:
            print(Fore.RED + "❌ Tidak ada pilihan. Ulangi...\n" + Style.RESET_ALL)
            continue

        mapping = {
            '1': 'axis',
            '2': 'telkomsel',
            '3': 'indosat',
            '4': 'tri',
            '5': 'smartfren',
            '6': 'ANY',  
        }

        operator = mapping.get(pilihan)
        if operator:
            return operator
        else:
            print(Fore.RED + "❌ Pilihan tidak valid. Ulangi...\n" + Style.RESET_ALL)
        
    mapping = {
    '1': 'axis',
    '2': 'telkomsel',
    '3': 'indosat',
    '4': 'tri',
    '5': 'smartfren',
    '6': 'ANY',  
    }
    return mapping.get(pilihan, None)  

def navigasi_akhir_farming():
    # Rainbow seperti tampilan awal
    rainbow = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    teks = "PILIH OPERATOR :\n"
    print()
    for i, char in enumerate(teks):
        warna = rainbow[i % len(rainbow)]
        print(warna + char, end='')
    print(Style.RESET_ALL)

    # Daftar operator seperti awal
    print(Fore.WHITE + "1. Axis     2. Telkomsel   3. Indosat")
    print("4. Three    5. Smartfren   6. Acak" + Style.RESET_ALL)

    # Prompt input seperti awal
    pilihan = input(Fore.YELLOW + "\nPilih / Back [b]: " + Style.RESET_ALL).strip().lower()

    if pilihan == "b":
        return
    elif pilihan in ["1", "2", "3", "4", "5", "6"]:
        mapping = {
            '1': 'axis',
            '2': 'telkomsel',
            '3': 'indosat',
            '4': 'three',
            '5': 'smartfren',
            '6': 'ANY'
        }
        operator = mapping.get(pilihan)
        if operator:
            mitra_key = "WA-CHECKER"
            api_key = get_next_key()
            if not api_key:
                print(Fore.RED + "❌ Tidak ada API key ditemukan di .keys." + Style.RESET_ALL)
                return
            jalankan_farming(api_key, mitra_key, operator)
            # setelah selesai farming → tampil ulang pilihan operator
            navigasi_akhir_farming()
    else:
        print(Fore.RED + "❌ Pilihan tidak valid." + Style.RESET_ALL)
        navigasi_akhir_farming()
        
auto_cancelled = False

def jalankan_farming(api_key, mitra_key, operator):
    import threading, time, requests
    service_id = 'ni'
    country_code = '6'
    PRODUCT_CODE = "gpc10"

    HEADERS_TEMPLATE = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': 'Bearer cermatiFrontend-37Dxq8fgAw+QeFmfCuRuUHAsnqUCaenmjxp1+MeksPM=',
        'content-type': 'application/json',
        'csrf-token': 'use-cookie',
        'origin': 'https://www.cermati.com',
        'priority': 'u=1, i',
        'referer': 'https://www.cermati.com/e-wallet',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
    }


    running = True
    current_number_id = None
    previous_status = ""
   
    def tunggu_koneksi():
        print(f"{rainbow_error()} Koneksi terputus. Menunggu koneksi kembali...")
        while True:
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                print(f"{rainbow_error()} Koneksi aman kembali Booss...")
                time.sleep(2)
                print(f"{rainbow_otp()} Melanjutkan polling status OTP...")
                return
            except OSError:
                time.sleep(3)
    
    def beli_nomor(api_key, operator):
        url = f"https://hero-sms.com/stubs/handler_api.php?action=getNumber&api_key={api_key}&service={service_id}&country={country_code}&operator={operator}&forward=0"
        while True:
            try:
                response = requests.get(url, timeout=10).text

                # 🔍 DETEKSI BANNED
                if "BANNED" in response.upper():
                    print(f"{red}[ERROR] Gagal beli nomor: {response}{reset}")
                    return None, None
                # ✅ PARSE NOMOR JIKA SUKSES
                if "ACCESS_NUMBER" in response:
                    _, id, nomor = response.strip().split(":")
                    print(f"{rainbow_info()} Nomor didapat: {green}{nomor}{reset} check...")
                    return id, nomor
                raise Exception(f"Gagal beli nomor: {red}{response}")
            except (requests.exceptions.RequestException, socket.error):
                tunggu_koneksi()
    
    def cancel_nomor(id):
        url = f"https://hero-sms.com/stubs/handler_api.php?api_key={api_key}&action=setStatus&status=8&id={id}"
        while True:
            try:
                requests.get(url, timeout=10)
                return
            except (requests.exceptions.RequestException, socket.error):
                tunggu_koneksi()
    
    def set_status_done(id):
        url = f"https://hero-sms.com/stubs/handler_api.php?api_key={api_key}&action=setStatus&status=6&id={id}"
        while True:
            try:
                requests.get(url, timeout=10)
                return
            except (requests.exceptions.RequestException, socket.error):
                tunggu_koneksi()
    
    def check_number_status(api_key, number_id):
        url = f"https://hero-sms.com/stubs/handler_api.php?api_key={api_key}&action=getStatus&id={number_id}"
        while True:
            try:
                return requests.get(url, timeout=10).text
            except (requests.exceptions.RequestException, socket.error):
                tunggu_koneksi()
      

    def cek_nomor_cermati(nomor):
        import requests
        nonlocal HEADERS_TEMPLATE  # pakai header global dari jalankan_farming

        url = "https://www.cermati.com/api/v1/digital-products/product/C-EWL-GPY-10000/billing-info"
        headers = HEADERS_TEMPLATE.copy()

        payload = {
            "productCode": "C-EWL-GPY-10000",
            "customerId": nomor
        }
        
        debug_print(Fore.CYAN + f"\n[DEBUG] Request ke Cermati untuk {nomor}")
        debug_print(Fore.LIGHTBLACK_EX + f"Payload: {payload}" + Style.RESET_ALL)
            
        response = requests.post(url, headers=headers, json=payload)
        debug_print(Fore.CYAN + f"[DEBUG] Status code: {response.status_code}")
        debug_print(Fore.LIGHTBLACK_EX + f"[DEBUG] Raw text: {response.text}\n" + Style.RESET_ALL)
            
        try:
            response_json = response.json()
            debug_print(Fore.YELLOW + "[DEBUG] JSON parsed:" + Style.RESET_ALL)
            debug_print(response_json)
            if response.status_code == 200:
                return True
            elif response.status_code == 500:
                return False
        except Exception as e:
            print(f"{rainbow_error()} Gagal cek nomor: {e}")
            pass

        return False
        
    running = True
    current_number_id = None
    previous_status = ""
    auto_cancelled = False

    def extract_otp_from_text(text):
        # Cari pola umum OTP: bisa "kode OTP", "OTP:", "kode", dsb
        match = re.search(r'(?:kode OTP|OTP|kode)\D*(\d{4,6})', text, re.IGNORECASE)
        if match:
            return match.group(1)
    
        # Fallback terakhir kalau nggak nemu format di atas, ambil 4-6 digit terakhir dari pesan
        fallback = re.findall(r'\b\d{4,6}\b', text)
        if fallback:
            return fallback[-1]
    
        return None
        
    def main_loop():
        nonlocal running, current_number_id, previous_status
        no_number_counter = 0

        while running:
            try:
                id_sms, nomor = beli_nomor(api_key, operator)
                no_number_counter = 0
                current_number_id = id_sms

                if not cek_nomor_cermati(nomor):
                    cancel_nomor(id_sms)
                    print(f"{rainbow_info()} Nomor tidak terdaftar, coba lagi...")
                    time.sleep(2)
                    continue
    
                print(f"{rainbow_info()} Nomor terdaftar, lanjut OTP...")

                while running:
                    status = check_number_status(api_key, current_number_id)
                    status_parts = status.split(':')
                    if len(status_parts) > 1:
                        status = status_parts[0]
    
                    if status == 'STATUS_OK':
                        raw_otp_msg = status_parts[-1].strip()
                        parsed_otp = extract_otp_from_text(raw_otp_msg)
                        if parsed_otp:
                            print(f"{rainbow_otp()} {Fore.GREEN}{parsed_otp}{Style.RESET_ALL}")
                        else:
                            print(f"{rainbow_otp()} {Fore.GREEN}{raw_otp_msg}{Style.RESET_ALL}")
    
                        # resend OTP
                        resend_url = f'https://hero-sms.com/stubs/handler_api.php?api_key={api_key}&action=setStatus&status=3&id={current_number_id}'
                        response = requests.get(resend_url)
                        if response.status_code == 200:
                            print(f"{rainbow_otp()} {Fore.YELLOW}SUCCESS_RESEND{Style.RESET_ALL}")
                            previous_status = ""
                        else:
                            print(f'GAGAL. {response.status_code}')
    
                    if status == 'STATUS_CANCEL':
                        print(f'{rainbow_otp()} {red}CANCELLED')
                        running = False
                        break
                    elif status != previous_status and status != 'STATUS_OK':
                        print(f'{rainbow_otp()} {status}')
                        previous_status = status
                    time.sleep(1)
            except Exception as e:
                print(f"{rainbow_error()} {e}")
                if "NO_NUMBERS" in str(e):
                    no_number_counter += 1
                    if no_number_counter == 3:
                        # AUTO CANCEL LEBIH DULU
                        if current_number_id:
                            try:
                                cancel_nomor(current_number_id)
                                print(f"{rainbow_auto()} Nomor dibatalkan....")
                                auto_cancelled = True  # Set flag auto_cancelled
                            except Exception as e:
                                print(f"{rainbow_warn()} Gagal batalkan nomor otomatis: {e}")
                        print("\n🔻Terlalu banyak NO_NUMBERS beruntun...")
                        print("❗Kemungkinan saldo kamu habis di smshub.org")
                        print("💡Silakan cek dashboard akun kamu dulu.")
                        time.sleep(2)
                        auto_cancelled = True
                        running = False
                        break
                else:
                    no_number_counter = 0
                time.sleep(1)
                continue

    main_thread = threading.Thread(target=main_loop)
    main_thread.start()
    main_thread.join(timeout=1)
    
    if auto_cancelled:
        main_thread.join()  # tunggu selesai total
        return
    
    # Tambahan delay pengecekan flag agar memberi waktu main_loop set flag
    for _ in range(3):  # maksimal 3x tunggu
        if auto_cancelled:
            main_thread.join()
            return
        time.sleep(0.5)
    
    if not running:
        main_thread.join()
        return  # keluar karena sudah diberhentikan manual
    
    # Jika tidak auto-cancel dan belum diberhentikan, baru minta input (untuk cancel manual)
    try:
        input('')
        running = False
        main_thread.join()
        if current_number_id:
            try:
                cancel_nomor(current_number_id)
                print(f"{rainbow_auto()} Nomor dibatalkan (manual).")
            except Exception as e:
                print(f"{rainbow_warn()} Gagal batalkan nomor manual: {e}")
    except KeyboardInterrupt:
        pass
      
# ====================== DASHBOARD HEROSMS======================

    
def input_api_key():
    path = ".keys"
    if os.path.exists(path):
        with open(path, "r") as f:
            keys = [line.strip() for line in f if line.strip()]
        if keys:
            print(f"\n✅ {len(keys)} APIKey ditemukan di {path}.")
            return  # tidak perlu input ulang
        else:
            print("⚠️ Apikey kosong. Silakan input ulang.")
    else:
        print("❌ File .keys. Silakan input API Key.")

    # kalau sampai sini artinya file belum ada atau kosong
    print("🔐 Input API Key HEROsms (multi support)")
    print("💡 Masukkan beberapa APIKey, satu per baris. Ketik 'done' kalau sudah.")

    keys = []
    while True:
        key = input(" ➤ APIKey: ").strip()
        if key.lower() == 'done':
            break
        if key:
            keys.append(key)
        else:
            print("⛔ APIKey tidak boleh kosong.")

    if not keys:
        print("❌ Tidak ada APIKey yang dimasukkan.")
        return

    with open(path, "w") as f:
        f.write("\n".join(keys))
    
    print(f"✅ {len(keys)} APIKey berhasil disimpan ke file {path}")
    
def ganti_apikey():
    path = ".keys"
    print("\n🛠️  GANTI API KEY (multi support)\n")
    
    if not os.path.exists(path):
        print("❌ File .keys belum ada.")
        return
    
    with open(path, "r") as f:
        keys = [line.strip() for line in f if line.strip()]

    if not keys:
        print("❌ File .keys kosong.")
        return

    print("📋 APIKeys saat ini:")
    for idx, key in enumerate(keys, 1):
        print(f"  {idx}. {key}")

    try:
        index = int(input("🔢 Pilih nomor APIKey: ")) - 1
        if index < 0 or index >= len(keys):
            print("❌ Nomor tidak valid.")
            return
    except ValueError:
        print("❌ Input harus angka.")
        return

    new_key = input("🆕 Masukkan APIKey baru: ").strip()
    if not new_key:
        print("❌ APIKey baru tidak boleh kosong.")
        return

    old_key = keys[index]
    keys[index] = new_key

    with open(path, "w") as f:
        f.write("\n".join(keys))

    print(f"✅ APIKey berhasil diganti:\n🧾 {old_key} ➜ {new_key}")
    
def animasi_loading():
    import sys
    import time
    print(Fore.YELLOW + Style.BRIGHT + "\nMemuat dashboard", end="", flush=True)
    for _ in range(6):
        time.sleep(0.2)
        print(".", end="", flush=True)
    print("" + Style.RESET_ALL)

from pathlib import Path
import sys, subprocess

BASE_DIR = Path(__file__).resolve().parent

def run_external_in(folder: str, filename: str, args=None):
    """Jalankan file Python di subfolder (cross-platform) dan baca seluruh isi foldernya."""
    folder_path = BASE_DIR / folder
    script_path = folder_path / filename
    if not script_path.exists():
        print(f"[!] File tidak ditemukan: {script_path}")
        return
    subprocess.run([sys.executable, str(script_path), *(args or [])],
                   cwd=str(folder_path), check=True)
    
def show_menu():
    print(Fore.BLUE + Style.BRIGHT + "\n M E N U :" + Style.RESET_ALL)
    print(Fore.GREEN + Style.BRIGHT + "\n  1. Gopay Games")
    print(Fore.GREEN + Style.BRIGHT + "  2. Mobapay Tool")
    print(Fore.GREEN + Style.BRIGHT + "  3. Lapak Gaming")
    print(Fore.GREEN + Style.BRIGHT + "  4. Topup NoLimit")
    print(Fore.GREEN + Style.BRIGHT + "  5. Voca Games")
    print(Fore.GREEN + Style.BRIGHT + "  6. Dunia Games")
    print(Fore.GREEN + Style.BRIGHT + "  7. Evos Topup")
    print(Fore.GREEN + Style.BRIGHT + "  8. Unipin Topup")
    print(Fore.GREEN + Style.BRIGHT + "  9. HEROsms x Mitra")
    print(Fore.GREEN + Style.BRIGHT + " 10. HEROsms OTP")
    print(Fore.GREEN + Style.BRIGHT + " 11. Litensi x Mitra")
    print(Fore.GREEN + Style.BRIGHT + " 12. Litensi.Id")
    print(Fore.GREEN + Style.BRIGHT + " 13. FastBit OTP")
    print(Fore.GREEN + Style.BRIGHT + " 14. SBower OTP")
    print(Fore.GREEN + Style.BRIGHT + " 15. SBower x Mitra")
    print(Fore.GREEN + Style.BRIGHT + " 16. Activate OTP")
    print(Fore.GREEN + Style.BRIGHT + " 17. Activate x Mitra")
    print(Fore.GREEN + Style.BRIGHT + " 18. PLN Checker")
    print(Fore.GREEN + Style.BRIGHT + " 19. Ganti API HEROsms")
    print(Fore.GREEN + Style.BRIGHT + "  0. Keluar" + Style.RESET_ALL)
    
    
def show_banner():
    animasi_loading()
    print(Fore.GREEN + Style.BRIGHT + """
███████╗███████╗████████╗ ██████╗  ██████╗ ██╗     
██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔═══██╗██║     
███████╗█████╗     ██║   ██║   ██║██║   ██║██║     
╚════██║██╔══╝     ██║   ██║   ██║██║   ██║██║     
███████║██║        ██║   ╚██████╔╝╚██████╔╝███████╗
╚══════╝╚═╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
    """ + Style.RESET_ALL)
    print(Fore.YELLOW + Style.BRIGHT + "     ╔════════════════════════════════════╗")
    print(Fore.YELLOW + Style.BRIGHT + "     ║      Selamat datang di Tools!      ║")
    print(Fore.YELLOW + Style.BRIGHT + "     ║     Author : Kings Faza | 2025     ║")
    print(Fore.YELLOW + Style.BRIGHT + "     ╚════════════════════════════════════╝" + Style.RESET_ALL)
    
    while True:
        show_menu()
        pilihan = input(Fore.BLUE + Style.BRIGHT + "\n Pilih Menu : " + Style.RESET_ALL).strip().lower()
        
        if pilihan == "1":
            run_external_in("GOGAMES", "GoGames1.34_Final.py")
        elif pilihan == "2":
            menu_moba()
        elif pilihan == "3":
            run_external_in("LAPAKGAMING", "Lapak_v1.11_Final.py")
        elif pilihan == "4":
            run_external_in("NOLIMIT", "NoLimit1.6.py")
        elif pilihan == "5":
            run_external_in("VOCAGAMES", "Vocagames1.7.py")
        elif pilihan == "6":
            run_external_in("DUNIAGAMES", "DGgames1.20.py")
        elif pilihan == "7":
            run_external_in("EVOSGG", "evos1.8.py")
        elif pilihan == "8":
            run_external_in("UNIPIN", "unipin1.7.py")
            
        elif pilihan == "9":
            farm_tool()
        elif pilihan == "10":
            batal = daftar_otp()
            if batal:
                continue
        elif pilihan == "11":
            run_external_in("BUKALAPAK", "LitensiFarm2.0.py")
        elif pilihan == "12":
            run_external_in("LITENSI", "Litensi1.6.py")
        elif pilihan == "13":
            run_external_in("FASTBIT", "menu_fastbit.py")
        elif pilihan == "14":
            run_external_in("SMSBOWER", "SMSbower1.0.py")
        elif pilihan == "15":
            run_external_in("BUKALAPAK", "SBowerFarm1.0.py")
        elif pilihan == "16":
            run_external_in("SMSACTIVE", "smsactivate_bot.py")
        elif pilihan == "17":
            print(f"\nCooming Soon Guys...")
            time.sleep(2)
        elif pilihan == "18":
            run_external_in("BUKALAPAK", "PLNChecker1.2.py")
        elif pilihan == "19":
            ganti_apikey()
        elif pilihan in {"0", "e"}:
            print(f"\nByee Byee Boskuuhhh...")
            break
        else:
            print("\nPilihan tidak valid.")
            input("Tekan ENTER untuk ulang...")


if __name__ == "__main__":
    input_api_key()
    show_banner()

