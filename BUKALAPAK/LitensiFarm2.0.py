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

# ===== DEBUG SWITCH =====
DEBUG = False  # ubah ke True kalau mau lihat semua debug print
def debug_print(msg):
    if DEBUG:
        print(msg)

if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios

from auto_mitra_bl_1_9 import refresh_and_save_to
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# simpan .farming di root BUKALAPAK (bukan di Litensi)
FARMING_FILE = os.path.join(BASE_DIR, ".farming")


def refresh_and_save_from_bukalapak(target_path):
    """Jalankan refresh di dalam folder BUKALAPAK agar cookies terbaca."""
    prev = os.getcwd()
    try:
        os.chdir(BASE_DIR)
        return refresh_and_save_to(target_path)
    finally:
        os.chdir(prev)
        
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
        
green = Fore.GREEN
red = Fore.RED
yellow = Fore.YELLOW

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
    print(Fore.CYAN + "Description: Litensi.Id x MitraBL " + Style.RESET_ALL)
    print(Fore.RED + "----------------------------------" + Style.RESET_ALL)


# ================== LITENSI API ==================
class LitensiAPI:
    BASE_URL = "https://litensi.id/api"

    def __init__(self, api_id: int, api_key: str):
        self.api_id = api_id
        self.api_key = api_key
        
    def get_profile(self):
        url = f"{self.BASE_URL}/profile"
        payload = {"api_id": self.api_id, "api_key": self.api_key}
        return requests.post(url, json=payload).json()
    
    def get_services(self):
        url = f"{self.BASE_URL}/sms/services"
        payload = {"api_id": self.api_id, "api_key": self.api_key}
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()

    def create_order(self, country, service, operator):
        url = f"{self.BASE_URL}/sms/order"
        payload = {
            "api_id": self.api_id,
            "api_key": self.api_key,
            "country": country,
            "service": service,
            "operator": operator
        }
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()

    def get_status(self, order_id: int):
        url = f"{self.BASE_URL}/sms/getstatus"
        payload = {"api_id": self.api_id, "api_key": self.api_key, "order_id": order_id}
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()

    def set_status(self, order_id: int, status: str):
        url = f"{self.BASE_URL}/sms/setstatus"
        payload = {
            "api_id": self.api_id,
            "api_key": self.api_key,
            "order_id": order_id,
            "status": status.upper()
        }
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
        
# ================== HELPER ==================
def save_litensi_cred():
    api_id = input("  🔏 Input API ID : ").strip()
    api_key = input("  🔐 Input API Key: ").strip()

    if not api_id or not api_key:
        print(f"{rainbow_warn()} API ID/Key kosong. Kembali ke menu utama...")
        return None, None

    with open(".litensi", "w") as f:
        f.write(f"api_id:{api_id}\n")
        f.write(f"api_key:{api_key}\n")

    print(f"{rainbow_info()} API Litensi disimpan ke .litensi ✅")
    return int(api_id), api_key


def load_litensi_cred():
    try:
        with open(".litensi", "r") as f:
            lines = f.read().strip().splitlines()
        creds = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                creds[k.strip()] = v.strip()
        api_id = int(creds.get("api_id", 0))
        api_key = creds.get("api_key", "")
        if not api_id or not api_key:
            raise ValueError("File .litensi tidak valid")
        return api_id, api_key
    except (FileNotFoundError, ValueError):
        print(f"{rainbow_error()} File .litensi kosong atau invalid.")
        return save_litensi_cred()

def get_balance(api: 'LitensiAPI'):
    prof = api.get_profile()
    if prof.get("success"):
        return prof["data"].get("balance", "0")
    return "0"
    
def check_balance(api: 'LitensiAPI'):
    try:
        prof = api.get_profile()
        if prof.get("success"):
            return prof["data"].get("balance", "0")
        return "0"
    except Exception as e:
        print(f"{rainbow_error()} Gagal ambil saldo: {e}")
        return "0"
        
def farm_tool():
    import colorama
    colorama.init(autoreset=True)
    from colorama import Fore, Style
    import base64
    import json
    import threading
    import os
    import time


    # ambil kredensial dari file .litensi
    api_id, api_key = load_litensi_cred()
    if not api_id or not api_key:
        return  # sudah ditangani di save_litensi_cred

    api = LitensiAPI(api_id, api_key)

    # --- Validasi saldo Litensi ---
    balance_str = get_balance(api)  # ambil saldo string
    try:
        balance = float(balance_str)
    except Exception:
        print(f"{rainbow_error()} {Fore.RED} Format saldo tidak valid: {balance_str}{Style.RESET_ALL}")
        return
    
    MIN_BALANCE = 2000.00  # minimal saldo (Rp)
    
    if balance < MIN_BALANCE:
        print(f"\n{rainbow_warn()} {Fore.RED} Saldo Anda Rp. {balance:,.2f} terlalu rendah. Minimum Rp. {MIN_BALANCE:,.2f} dibutuhkan.{Style.RESET_ALL}")
        print(Fore.LIGHTBLACK_EX + "[SILAKAN ISI SALDO DULU DAN COBA LAGI]")
        return
    
    print(f"\n{rainbow_info()} {Fore.GREEN}Saldo Litensi : Rp. {balance:,.2f}{Style.RESET_ALL}")
        
    mitra_key = load_token_farming()
    mitra_key = sanitize_token(mitra_key)
    if not mitra_key:
        return
    print_farming_ascii()
    operator = load_operator_farm()
    if not operator:
        return 
    print(Style.BRIGHT + Fore.MAGENTA + "\nFARMING DIMULAI BOSSKUHHH..." + Style.RESET_ALL)

    jalankan_farming(api, mitra_key, operator)
    navigasi_akhir_farming(api)
       
def load_token_farming():
    # 1) Kalau ada file .farming → coba pakai
    if os.path.exists(FARMING_FILE):
        with open(FARMING_FILE, "r") as f:
            raw = f.read()
        token = sanitize_token(raw)
        try:
            parts = token.split(".")
            if len(parts) < 3:
                raise ValueError("Format JWT tidak lengkap")
            payload_part = parts[1]
            # pad base64
            rem = len(payload_part) % 4
            if rem != 0:
                payload_part += "=" * (4 - rem)
            decoded = json.loads(base64.urlsafe_b64decode(payload_part.encode("utf-8")).decode("utf-8"))
            exp = int(decoded.get("exp", 0))

            # info TTL (WIB)
            show_token_expiry(exp)

            # masih valid → langsung pakai
            if exp > int(time.time()):
                return token

            print(f"{rainbow_warn()} Token kadaluarsa. Mencoba refresh otomatis...")
            auto_tok = refresh_token_to_farming()
            if auto_tok:
                # tampilkan TTL token baru
                try:
                    pp = auto_tok.split(".")[1]
                    if len(pp) % 4 != 0:
                        pp += "=" * (4 - (len(pp) % 4))
                    show_token_expiry(json.loads(base64.urlsafe_b64decode(pp).decode("utf-8")).get("exp", 0))
                except Exception:
                    pass
                return auto_tok

        except Exception:
            print(f"{rainbow_error()} Token invalid. Coba refresh otomatis...")
            auto_tok = refresh_token_to_farming()
            if auto_tok:
                try:
                    pp = auto_tok.split(".")[1]
                    if len(pp) % 4 != 0:
                        pp += "=" * (4 - (len(pp) % 4))
                    show_token_expiry(json.loads(base64.urlsafe_b64decode(pp).decode("utf-8")).get("exp", 0))
                except Exception:
                    pass
                return auto_tok

            # Fallback terakhir: coba ambil dari mitra_bearer.json jika ada
            try:
                if os.path.exists("mitra_bearer.json"):
                    data = json.load(open("mitra_bearer.json", "r"))
                    from_json = sanitize_token(data.get("access_token") or data.get("bearer"))
                    if from_json:
                        with open(FARMING_FILE, "w") as f:
                            f.write(from_json)
                        print(f"{rainbow_info()} Ambil token dari mitra_bearer.json → .farming ✅")
                        return from_json
            except Exception:
                pass

    # 2) Kalau .farming belum ada → langsung coba refresh otomatis
    print(f"{rainbow_info()} Token kosong. Refresh otomatis dari ServerMitra...")
    auto_tok = refresh_token_to_farming()
    if auto_tok:
        try:
            pp = auto_tok.split(".")[1]
            if len(pp) % 4 != 0:
                pp += "=" * (4 - (len(pp) % 4))
            show_token_expiry(json.loads(base64.urlsafe_b64decode(pp).decode("utf-8")).get("exp", 0))
        except Exception:
            pass
        return auto_tok

    # 3) Refresh gagal → barulah minta manual
    return save_token_farming()

def refresh_token_to_farming() -> str | None:
    try:
        new_tok = refresh_and_save_from_bukalapak(FARMING_FILE)
        print(f"{rainbow_info()} Token ServerMitra di-refresh otomatis")
        print(f"{rainbow_info()} Token disimpan ke .farming ✅")
        return new_tok
    except Exception as e:
        print(f"{rainbow_error()} Gagal refresh otomatis: {e}")
        print(f"{rainbow_error()} Gagal refresh otomatis: {e}")
        return None
        
def sanitize_token(raw: str) -> str:
    """Bersihin token dari spasi/kutip/prefix 'Bearer '."""
    if raw is None:
        return ""
    t = str(raw).strip()
    if t.startswith('"') and t.endswith('"'):
        t = t[1:-1]
    if t.lower().startswith("bearer "):
        t = t.split(" ", 1)[1].strip()
    return t

def show_token_expiry(exp: int):
    """Cetak waktu expired (WIB) + selisih pakai 'lagi' atau 'lalu'."""
    import datetime as _dt

    tz = _dt.timezone(_dt.timedelta(hours=7))  # WIB
    now = _dt.datetime.now(tz)
    dt  = _dt.datetime.fromtimestamp(int(exp), tz)
    delta_s = int((dt - now).total_seconds())

    # humanize (jam & menit saja)
    s = abs(delta_s)
    jam = s // 3600
    menit = (s % 3600) // 60
    parts = []
    if jam:
        parts.append(f"{jam} jm")
    parts.append(f"{menit} mnt")
    arah = "lagi" if delta_s >= 0 else "lalu"
    human = " ".join(parts) + f" {arah}"

    msg = (f" Expired: {dt:%Y-%m-%d %H:%M:%S} WIB (± {human})")
    if delta_s < 0:
        print(rainbow_warn() + msg)   # [EROR]
    else:
        print(rainbow_info()  + msg)   # [INFO]
    
def save_token_farming():
    new_token = input("🔐 Masukkan token ServerMitra: ").strip()
    
    if not new_token:  # cek kosong
        print(f"{rainbow_warn()} Token Kosong. Kembali ke menu utama...\n")
        return None

    new_token = sanitize_token(new_token)   # <— tambahkan ini
    with open(FARMING_FILE, "w") as f:
        f.write(new_token)
    print(f"{rainbow_info()} Token disimpan ke .farming\n")
    return new_token
    
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
            print(Fore.RED + "❌ Tidak ada pilihan. Ulangi..." + Style.RESET_ALL)
            continue

        mapping = {
            '1': 'axis',
            '2': 'telkomsel',
            '3': 'indosat',
            '4': 'three',
            '5': 'smartfren',
            '6': 'any',  
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
    '4': 'three',
    '5': 'smartfren',
    '6': 'any',  
    }
    return mapping.get(pilihan, None)  

def navigasi_akhir_farming(api):
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
            '6': 'any'
        }
        operator = mapping.get(pilihan)
        if operator:
            print(Style.BRIGHT + Fore.MAGENTA + "\nFARMING DIMULAI BOSSKUHHH..." + Style.RESET_ALL)
            mitra_key = load_token_farming()
            mitra_key = sanitize_token(mitra_key)

            jalankan_farming(api, mitra_key, operator)

            navigasi_akhir_farming(api)
    else:
        print(Fore.RED + "❌ Pilihan tidak valid." + Style.RESET_ALL)
        navigasi_akhir_farming(api)
        
def jalankan_farming(api: 'LitensiAPI', mitra_key, operator):
    import threading, time, requests
    service_id = '348'
    country_code = '7'
    PRODUCT_CODE = "gpc10"

    mitra_key = sanitize_token(mitra_key)
    
    HEADERS_TEMPLATE = {
    "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {mitra_key}",
        "Origin": "https://app.servermitra.com",
        "Referer": "https://app.servermitra.com/"
    }

    running = True
    current_number_id = None
    previous_status = ""
   
    def tunggu_koneksi(pesan_khusus=""):
        print(f"{rainbow_error()} Koneksi terputus. Menunggu koneksi kembali")
        while True:
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                print(f"{rainbow_info()} Koneksi aman kembali Booss")
                time.sleep(2)
                if pesan_khusus:
                    print(Fore.CYAN + pesan_khusus + Style.RESET_ALL)
                return
            except OSError:
                time.sleep(3)
    
    def beli_nomor(api: LitensiAPI, service_id, operator: str):
        while True:
            try:
                order = api.create_order(country=7, service=348, operator=operator)
        
                if not order.get("success"):
                    reason = order.get("data", "UNKNOWN ERROR")
                    print(f"{rainbow_warn()} Gagal beli nomor: {reason}")
                    return None, None
        
                data = order["data"]
                order_id = data["order_id"]
                nomor = data["phone"]
        
                print(f"{rainbow_info()} Nomor didapat: {Fore.GREEN}{nomor}{Style.RESET_ALL}")
                return order_id, nomor
        
            except (requests.ConnectionError, requests.Timeout) as e:
                tunggu_koneksi(f"{rainbow_info()} Melanjutkan order nomor...")
                return None, None
            except Exception as e:
                debug_print(f"{rainbow_error()} Error tak terduga saat beli nomor: {e}")
                return None, None
    
    def cancel_nomor(api: LitensiAPI, order_id):
        if not order_id:
            return None
        while True:
            try:
                url = f"{api.BASE_URL}/sms/setstatus"
                payload = {
                    "api_id": api.api_id,
                    "api_key": api.api_key,
                    "order_id": order_id,
                    "status": "CANCELED"
                }
    
                r = requests.post(url, json=payload, timeout=10)
    
                # kalau server kasih status error (404/500), jangan diulang
                if r.status_code >= 400:
                    debug_print(f"{rainbow_warn()} Gagal cancel nomor: {r.status_code} {r.text}")
                    return None
    
                r.raise_for_status()
                return r.json()
    
            except (requests.ConnectionError, requests.Timeout):
                tunggu_koneksi(f"{rainbow_info()} Melanjutkan cancel orderan...")
                # setelah koneksi balik → coba lagi (loop lanjut)
    
            except Exception as e:
                debug_print(f"{rainbow_warn()} Gagal cancel nomor: {e}")
                return None
            
    def success_nomor(api: LitensiAPI, order_id):
        try:
            url = f"{api.BASE_URL}/sms/setstatus"
            payload = {
                "api_id": api.api_id,
                "api_key": api.api_key,
                "order_id": order_id,
                "status": "SUCCESS"
            }
            
            r = requests.post(url, json=payload, timeout=10)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            debug_print(f"{rainbow_warn()} Gagal cancel nomor: {e}")
            return None
            
    
    def check_number_status(api: LitensiAPI, order_id):
        while True:
            try:
                res = api.get_status(order_id)
                if res.get("success") and "data" in res:
                    return res["data"]["status"], res["data"].get("sms", "")
                else:
                    debug_print(f"{rainbow_warn()} Gagal cek status API: {res}")
                    return None, None
            except (requests.ConnectionError, requests.Timeout) as e:
                tunggu_koneksi(f"{rainbow_otp()} Melanjutkan polling status OTP...")
            except Exception as e:
                # error selain itu
                debug_print(f"{rainbow_error()} Error tak terduga saat cek status: {e}")
                return None, None

            
    def cek_nomor_servermitra(nomor):
        nonlocal HEADERS_TEMPLATE, mitra_key  # biar bisa update
        headers = HEADERS_TEMPLATE.copy()
        payload = {"customer_number": nomor, "product_code": PRODUCT_CODE}
        try:
            response = requests.post(
                "https://api.servermitra.com/v1/end-user-transactions/inquiry",
                json=payload, headers=headers, timeout=30
            )
    
            # Jika token expired/invalid -> refresh + retry sekali
            if (response.status_code == 401) or ("expired" in response.text.lower()) or ("invalid token" in response.text.lower()):
                new_tok = refresh_token_to_farming()
                if new_tok:
                    mitra_key = sanitize_token(new_tok)
                    HEADERS_TEMPLATE["Authorization"] = f"Bearer {mitra_key}"
                    headers["Authorization"] = HEADERS_TEMPLATE["Authorization"]
    
                    response = requests.post(
                        "https://api.servermitra.com/v1/end-user-transactions/inquiry",
                        json=payload, headers=headers, timeout=30
                    )
    
            if response.status_code == 200:
                data = response.json()
                status = data.get("end_user_transaction_inquiry", {}).get("status")
                return status != "END_USER_TRANSACTION_INQUIRY_STATUS_FAILED"
    
        except Exception as e:
            debug_print(f"{rainbow_error()} Gagal cek nomor: {e}")
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

    otp_received_count = 0
    def main_loop():
        nonlocal running, current_number_id, previous_status, auto_cancelled, otp_received_count
        no_number_counter = 0
        while running:
            try:
                id_sms, nomor = beli_nomor(api, service_id, operator)
                no_number_counter = 0
                current_number_id = id_sms
    
                if not cek_nomor_servermitra(nomor):
                    cancel_nomor(api, id_sms)
                    print(f"{rainbow_info()} Nomor tidak terdaftar, coba lagi...")
                    time.sleep(1)
                    continue
    
                print(f"{rainbow_info()} Nomor terdaftar, lanjut OTP...")

                otp_received_count = 0
                
                while running:
                    status, sms = check_number_status(api, current_number_id)
                    
                    if status == "WAITING":
                        if previous_status != "WAITING":
                            print(f"{rainbow_otp()} WAITING")
                            previous_status = "WAITING"
                    
                    elif status == "RECEIVED":
                        raw_otp_msg = sms.strip() if sms else ""
                        parsed_otp = extract_otp_from_text(raw_otp_msg)
                        if parsed_otp:
                            print(f"{rainbow_otp()}{Fore.GREEN} {parsed_otp}{Style.RESET_ALL}")
                        else:
                            print(f"{rainbow_otp()}{Fore.YELLOW} {raw_otp_msg}{Style.RESET_ALL}")
                    
                        # request resend ke Litensi
                        api.set_status(current_number_id, "RESEND")
                        print(f"{rainbow_otp()}{Fore.YELLOW} SUCCESS_RESEND{Style.RESET_ALL}")
                        otp_received_count += 1
                        previous_status = "SUCCESS_RESEND"
                    
                    elif status == "SUCCESS":
                        print(f"{rainbow_otp()}{Fore.GREEN} DONE{Style.RESET_ALL}")
                        running = False
                        break
                    
                    elif status == "CANCELED":
                        print(f"{rainbow_otp()}{Fore.RED} CANCELED{Style.RESET_ALL}")
                        if current_number_id:
                            cancel_resp = cancel_nomor(api, current_number_id)
                        running = False
                        break
                    elif status != previous_status and status != 'WAITING':
                        print(f'{rainbow_otp()} {status}')
                        previous_status = status
                        
                    time.sleep(2)
            except Exception as e:
                print(f"{rainbow_error()} {e}")
                if "NO_NUMBERS" in str(e):
                    no_number_counter += 1
                    if no_number_counter == 5:
                        # AUTO CANCEL LEBIH DULU
                        if current_number_id:
                            try:
                                cancel_nomor(api, current_number_id)
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
                if otp_received_count > 0:
                    success_nomor(api, current_number_id)
                    print(f"{rainbow_info()} Nomor ditandai sukses (manual).")
                else:
                    cancel_nomor(api, current_number_id)
                    print(f"{rainbow_info()} Nomor dibatalkan (manual).")
            except Exception as e:
                debug_print(f"{rainbow_warn()} Gagal set status nomor manual: {e}")
    except KeyboardInterrupt:
        pass
  

# ========== MAIN ==========
def main():
    farm_tool()

if __name__ == "__main__":
    main()