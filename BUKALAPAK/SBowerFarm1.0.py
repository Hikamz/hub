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

# **** Warna Global ****
green = Fore.GREEN
red = Fore.RED
yellow = Fore.YELLOW
blue = Fore.BLUE
reset = Fore.RESET

# ===== DEBUG SWITCH =====
DEBUG_MODE = False
def debug_print(*args, **kwargs):
    if DEBUG_MODE:
        print(f"{rainbow_debug()}", *args, **kwargs)

if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios

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
 
def rainbow_debug():
        return (Fore.RED + "[" + Fore.YELLOW + "D" + Fore.GREEN + "B" + Fore.CYAN + "U" + Fore.MAGENTA + "G" + Fore.RED + "]" + Fore.RESET)
             
def print_farming_ascii():
    print(Fore.GREEN  + "\n███████  " + Fore.YELLOW + "█████  " + Fore.CYAN   + "███████  " + Fore.RED    + "███  ███")
    print(Fore.GREEN  + "██      " + Fore.YELLOW + "██   ██ " + Fore.CYAN   + "██   ██ " + Fore.RED    + "████  ████")
    print(Fore.GREEN  + "█████   " + Fore.YELLOW + "███████ " + Fore.CYAN   + "██████  " + Fore.RED    + "██ ████ ██")
    print(Fore.GREEN  + "██      " + Fore.YELLOW + "██   ██ " + Fore.CYAN   + "██   ██ " + Fore.RED    + "██  ██  ██")
    print(Fore.GREEN  + "██      " + Fore.YELLOW + "██   ██ " + Fore.CYAN   + "██   ██ " + Fore.RED    + "██      ██" + Fore.RESET)
    print(Fore.GREEN + "----------------------------------" + Style.RESET_ALL)
    print(Fore.YELLOW + "    Author: Kings Faza | 2025   " + Style.RESET_ALL)
    print(Fore.CYAN + " Description: SMSBower x Cermati " + Style.RESET_ALL)
    print(Fore.RED + "----------------------------------" + Style.RESET_ALL)


# ========== API CLIENT LITENSI ==========
class SmsBowerAPI:
    BASE_URL = "https://smsbower.online/stubs/handler_api.php"

    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_balance_raw(self):
        url = f"{self.BASE_URL}?api_key={self.api_key}&action=getBalance"
        r = requests.get(url, timeout=10)
        return r.text  # contoh: ACCESS_BALANCE:0.95
        
    def create_order(self, country: int, service: str, max_price: float = None, provider_ids=None):
        """
        Membuat order baru di SMSBower (pakai getNumberV2).
        """
        url = self.BASE_URL
        params = {
            "api_key": self.api_key,
            "action": "getNumberV2",
            "service": service,
            "country": country
        }
        if max_price:
            params["maxPrice"] = max_price
        if provider_ids:
            if isinstance(provider_ids, list):
                params["providerIds"] = ",".join(str(p) for p in provider_ids)
            else:
                params["providerIds"] = str(provider_ids)
    
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
    
            if "activationId" in data and "phoneNumber" in data:
                return {
                    "activationId": data["activationId"],
                    "phoneNumber": data["phoneNumber"],
                    "activationCost": data.get("activationCost"),
                    "countryCode": data.get("countryCode"),
                    "canGetAnotherSms": data.get("canGetAnotherSms"),
                    "activationTime": data.get("activationTime"),
                }
            else:
                return {"error": data}
        except Exception as e:
            return {"error": str(e)}
        
    def get_status(self, activation_id: int):
        url = "https://smsbower.online/stubs/handler_api.php"
        params = {
            "api_key": self.api_key,
            "action": "getStatus",
            "id": activation_id
        }
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            return r.text.strip()
        except (requests.exceptions.RequestException, OSError):
            # 🔇 Tidak usah print error apa pun di sini
            return "ERROR_CONN"
                
        
    def set_status(self, activation_id: int, status: str):
        mapping = {
            "SMS_SENT": 1,
            "RETRY": 3,
            "SUCCESS": 6,
            "CANCEL": 8,
        }
        status_code = mapping.get(status.upper())
        if not status_code:
            return f"Unknown status: {status}"
    
        url = "https://smsbower.online/stubs/handler_api.php"
        params = {
            "api_key": self.api_key,
            "action": "setStatus",
            "id": activation_id,
            "status": status_code
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.text.strip()
    

        
# ================== HELPER ==================
def save_smsbower_cred():
    api_key = input("  🔐 Input API Key: ").strip()

    if not api_key:
        print(f"{rainbow_warn()} API Key kosong. Kembali ke menu utama...")
        return None

    with open(".smsbower", "w") as f:
        f.write(f"api_key:{api_key}\n")

    print(f"{rainbow_info()} API SMSBower disimpan ke .smsbower ✅")
    return api_key


def load_smsbower_cred():
    try:
        with open(".smsbower", "r") as f:
            lines = f.read().strip().splitlines()
        creds = {}
        for line in lines:
            if ":" in line:
                k, v = line.split(":", 1)
                creds[k.strip()] = v.strip()
        api_key = creds.get("api_key", "")
        if not api_key:
            raise ValueError("File .smsbower tidak valid")
        return api_key
    except (FileNotFoundError, ValueError):
        print(f"{rainbow_warn()} File .smsbower kosong atau invalid.")
        return save_smsbower_cred()

def get_balance(api: 'SmsBowerAPI'):
    res = api.get_balance_raw()
    if res.startswith("ACCESS_BALANCE:"):
        try:
            return float(res.split(":")[1])
        except:
            return 0.0
    return 0.10

def delayed_cancel(api, activation_id, number, delay):
    time.sleep(delay)
    try:
        api.set_status(activation_id, "CANCEL")
        pass
    except Exception as e:
        print(f"{rainbow_otp()} Gagal membatalkan nomor {number}: {e}")  
        
    
def check_balance(api: 'SmsBowerAPI'):
    try:
        raw = api.get_balance_raw().strip()

        # Format normal: ACCESS_BALANCE:0.9058
        if raw.startswith("ACCESS_BALANCE:"):
            return raw.split(":")[1]

        # Format error dari server
        print(f"{rainbow_error()} Gagal ambil saldo: {raw}")
        return "0"

    except Exception as e:
        print(f"{rainbow_error()} Gagal ambil saldo: {e}")
        return "0"
        
def nomor_62_to_08(nomor):
    nomor = str(nomor)
    if nomor.startswith("62"):
        return "0" + nomor[2:]
    return nomor
    
def farm_tool():
    import colorama
    colorama.init(autoreset=True)
    from colorama import Fore, Style
    import base64, json, threading, os, time

    # 🔹 Ambil kredensial dari file .smsbower
    api_key = load_smsbower_cred()
    if not api_key:
        print(f"{rainbow_error()} Kredensial SMSBower belum diset. Silakan login dulu.")
        save_smsbower_cred()  # auto prompt input API ID dan Key
        api_key = load_smsbower_cred()
        if not api_key:
            print(f"{rainbow_error()} Gagal memuat API Key. Keluar...")
            return

    # 🔹 Inisialisasi API
    api = SmsBowerAPI(api_key=api_key)

    # 🔹 Cek saldo
    balance_str = check_balance(api)
    try:
        balance = float(balance_str)
    except Exception:
        print(f"{rainbow_error()}{Fore.RED} Format saldo tidak valid: {balance_str}{Style.RESET_ALL}")
        return

    # 🔹 Minimal saldo (USD, karena SMSBower pakai dollar)
    MIN_BALANCE = 0.040  # bisa kamu ubah sesuai kebutuhan farming

    if balance < MIN_BALANCE:
        print(f"\n{rainbow_warn()}{Fore.RED} Saldo Anda ${balance:.4f} terlalu rendah.")
        print(f"Minimum saldo ${MIN_BALANCE:.4f} dibutuhkan.{Style.RESET_ALL}")
        print(Fore.LIGHTBLACK_EX + "[ISI SALDO DULU DAN COBA LAGI]")
        return

    print(f"\n{rainbow_info()} {Fore.GREEN}Saldo SMSBower : Rp. {balance:,.4f}{Style.RESET_ALL}")
        
    mitra_key = "WA-CHECKER"
    print_farming_ascii()
    operator = load_provider_list(api_key=api_key, service="ni", country=6)
    if not operator or operator == "b":
        print(f"{rainbow_info()} Kembali ke menu utama...\n")
        return
    print(Style.BRIGHT + Fore.MAGENTA + "\nFARMING DIMULAI BOSSKUHHH..." + Style.RESET_ALL)

    jalankan_farming(api, mitra_key, operator)
    navigasi_akhir_farming(api)
       
    
def load_provider_list(api_key: str, service: str, country: int = 6):
    """
    Ambil list provider dari SMSBower (getPricesV3) untuk service & country tertentu.
    """
    url = "https://smsbower.online/stubs/handler_api.php"
    params = {
        "api_key": api_key,
        "action": "getPricesV3",
        "service": service,
        "country": country
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(Fore.RED + f"[ERROR] Gagal ambil provider list: {e}" + Style.RESET_ALL)
        return None

    if str(country) not in data or service not in data[str(country)]:
        print(Fore.RED + "[ERROR] Data provider kosong." + Style.RESET_ALL)
        return None

    providers = data[str(country)][service]

    # Tampilan judul rainbow-style
    rainbow = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    teks = "PILIH PROVIDER :\n"
    print()
    for i, char in enumerate(teks):
        warna = rainbow[i % len(rainbow)]
        print(warna + char, end='')
    print(Style.RESET_ALL)

    mapping = {}
    idx = 1
    
    # 🔽 ambil provider yang stok >= 200
    filtered = [
        (pid, info)
        for pid, info in providers.items()
        if info.get("count", 0) >= 200
    ]
    
    # 🔽 SORT harga termurah → termahal
    filtered.sort(key=lambda x: float(x[1].get("price", 0)))
    
    for pid, info in filtered:
        price = info.get("price")
        count = info.get("count", 0)
    
        print(f"{idx}. {pid} | 💲 {price} | 📦 {count}")
        mapping[str(idx)] = pid
        idx += 1

    while True:
        pilihan = input(Fore.YELLOW + "\nPilih / Back [b]: " + Style.RESET_ALL).strip().lower()
        if pilihan == "b":
            return "b"
        if pilihan in mapping:
            return mapping[pilihan]
        print(Fore.RED + "Pilihan tidak valid." + Style.RESET_ALL)  

def navigasi_akhir_farming(api):
    # Langsung balik ke daftar provider
    time.sleep(1)
    api_key = api.api_key
    operator = load_provider_list(api_key=api_key, service="ni", country=6)
    if operator == "b":
        print(f"{rainbow_info()} Kembali ke menu utama...\n")
        return
    if operator:
        print(Style.BRIGHT + Fore.MAGENTA + "\nFARMING DIMULAI BOSSKUHHH..." + Style.RESET_ALL)
        mitra_key = "WA-CHECKER"

        jalankan_farming(api, mitra_key, operator)

        navigasi_akhir_farming(api)
    else:
        print(Fore.RED + "❌ Pilihan tidak valid." + Style.RESET_ALL)
        navigasi_akhir_farming(api)
        
def jalankan_farming(api: 'SmsBowerAPI', mitra_key, operator):
    import threading, time, requests
    service_id = 'ni'
    country_code = '6'
    
    nomor = None
    mitra_key = "WA-CHECKER"
    
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
    current_activation_id = None
    previous_status = ""
    otp_received_count = 0
    auto_cancelled = False
    
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
    
    def beli_nomor(api: SmsBowerAPI, operator_id):
        try:
            res = api.create_order(country=6, service="ni", provider_ids=operator_id)
    
            # jika respons berupa teks string, bukan JSON
            if isinstance(res, str):
                if "NO_NUMBERS" in res:
                    print(f"{rainbow_warn()} Stok nomor kosong di SMSBower.")
                    time.sleep(1)
                    return None, None
                elif "NO_BALANCE" in res:
                    print(f"{rainbow_warn()} Saldo SMSBower habis, isi dulu ya!")
                    time.sleep(1)
                    return None, None
                elif "NO_SERVICE" in res:
                    print(f"{rainbow_warn()} Service tidak tersedia di SMSBower.")
                    time.sleep(1)
                    return None, None
                else:
                    print(f"{rainbow_warn()} Respons tidak dikenali: {res}")
                    time.sleep(3)
                    return None, None
    
            # jika hasil sudah JSON / dict
            if "activationId" in res:
                activation_id = res["activationId"]
                nomor = res["phoneNumber"]
                print_loading(
                    f"{rainbow_info()} Mencoba nomor "
                    f"{Fore.GREEN}{nomor_62_to_08(nomor)}{Style.RESET_ALL}"
                )
                return activation_id, nomor
            else:
                err = res.get("error", "UNKNOWN ERROR")
                print(f"{rainbow_warn()} Gagal beli nomor: {err}")
                return None, None
    
        except Exception as e:
            print(f"{rainbow_error()} Error beli nomor: {e}")
            time.sleep(3)
            return None, None

    def cancel_nomor(api, activation_id):
        try:
            res = api.set_status(activation_id, "CANCEL")
            pass
        except Exception as e:
            print(f"{rainbow_warn()} Gagal cancel nomor: {e}")

    def success_nomor(api, activation_id):
        try:
            res = api.set_status(activation_id, "SUCCESS")
            print(f"{rainbow_info()} {green}DONE")
        except Exception as e:
            print(f"{rainbow_warn()} Gagal sukses: {e}")
            
    
    def check_number_status(api, activation_id):
        """
        Wrapper universal agar bisa dipakai Litensi & SMSBower
        """
        try:
            res = api.get_status(activation_id)
            if isinstance(res, dict):  # Mode Litensi lama
                if res.get("success"):
                    return res["data"]["status"], res["data"].get("sms", "")
            else:  # Mode SMSBower plain text
                if res.startswith("STATUS_OK"):
                    return "STATUS_OK", res.split(":", 1)[1] if ":" in res else ""
                return res.strip(), ""
        except Exception as e:
            debug_print(f"{rainbow_error()} Gagal cek status: {e}")
        return None, None

            
    def cek_nomor_cermati(nomor):
        import requests
        nonlocal HEADERS_TEMPLATE

        url = "https://www.cermati.com/api/v1/digital-products/product/C-EWL-GPY-10000/billing-info"
        headers = HEADERS_TEMPLATE.copy()

        payload = {
            "productCode": "C-EWL-GPY-10000",
            "customerId": nomor
        }
        
        debug_print(Fore.CYAN + f"[DEBUG] Request ke Cermati untuk {nomor}")
        debug_print(Fore.LIGHTBLACK_EX + f"Payload: {payload}" + Style.RESET_ALL)
            
        response = requests.post(url, headers=headers, json=payload)
        debug_print(Fore.CYAN + f"[DEBUG] Status code: {response.status_code}")
            
        try:
            response_json = response.json()
            debug_print(Fore.YELLOW + "[DEBUG] JSON parsed:" + Style.RESET_ALL)
            debug_print(Fore.LIGHTBLACK_EX + f"{response_json}" + Style.RESET_ALL)
            if response.status_code == 200:
                return True
            elif response.status_code == 500:
                return False
        except Exception as e:
            print(f"{rainbow_error()} Gagal cek nomor: {e}")
            pass

        return False

    running = True
    current_activation_id = None
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

    def print_loading(msg):
        sys.stdout.write("\r\033[K" + msg)
        sys.stdout.flush()

    def commit_loading_line():
        # turunin baris setelah loading, biar baris "mencoba nomor ..." tetap terlihat
        sys.stdout.write("\n")
        sys.stdout.flush()
        
    otp_received_count = 0
    def main_loop():
        nonlocal running, current_activation_id, previous_status, auto_cancelled, otp_received_count
        no_number_counter = 0
        last_otp_text = None
        same_otp_count = 0
        
        while running:
            nonlocal nomor
            id_sms, nomor = beli_nomor(api, operator)
            if not id_sms:
                time.sleep(1)
                continue
            no_number_counter = 0
            current_activation_id = id_sms

            if not cek_nomor_cermati(nomor):
                print_loading(f"{rainbow_info()} Nomor tidak terdaftar, skip...")
                threading.Thread(
                    target=delayed_cancel,
                    args=(api, id_sms, nomor, 120),
                    daemon=True
                ).start()
                time.sleep(1)
                continue

            commit_loading_line()
            print(f"{rainbow_info()} Nomor terdaftar, lanjut OTP...")

            otp_received_count = 0
            previous_status = ""
            last_otp_text = None
            same_otp_count = 0
            
            while running:
                try:
                    status_text = api.get_status(current_activation_id)
                    if status_text == "ERROR_CONN":
                        tunggu_koneksi(
                            f"{rainbow_otp()} Melanjutkan polling OTP {green}{nomor_62_to_08(nomor)}{reset}"
                        )
                        previous_status = ""
                        time.sleep(2)
                        continue
                except Exception as e:
                    print(f"{rainbow_error()} {e}")
                    time.sleep(2)
                    continue
                
                if status_text == "STATUS_WAIT_CODE":
                    if previous_status != "WAIT_CODE":
                        print(f"{rainbow_otp()} {Fore.YELLOW}WAITING{Style.RESET_ALL}")
                        previous_status = "WAIT_CODE"
                
                elif status_text.startswith("STATUS_OK"):
                    otp_received_count += 1
                    pesan = status_text.split(":", 1)[1].strip() if ":" in status_text else ""
                    kode_otp = extract_otp_from_text(pesan)
                    otp_text = kode_otp or pesan
                    
                    if otp_text == last_otp_text:
                        same_otp_count += 1
                    
                        # kalau OTP yang sama keulang, jangan print & jangan resend
                        if same_otp_count >= 3:
                            print(f"{rainbow_otp()} {red}CANCELED{reset}")
                            running = False
                            break
                    
                        time.sleep(2)
                        continue
                    else:
                        last_otp_text = otp_text
                        same_otp_count = 0
                    if kode_otp:
                        print(f"{rainbow_otp()} {Fore.GREEN}{kode_otp}{Style.RESET_ALL}")
                    else:
                        print(f"{rainbow_otp()} {Fore.YELLOW}{pesan}{Style.RESET_ALL}")
                    # kirim status retry biar bisa lanjut terima SMS baru
                    api.set_status(current_activation_id, "RETRY")
                    print(f"{rainbow_otp()} {yellow}SUCCESS_RESEND{reset}")
                    previous_status = "RETRY"

                elif any(x in status_text for x in ["STATUS_SUCCESS", "STATUS_OK", "STATUS_FINISHED", "ACCESS_READY"]):
                    print(f"{rainbow_otp()}{green}DONE{reset}")
                    running = False
                    time.sleep(1)
                    break
                
                elif any(x in status_text for x in ["STATUS_CANCEL", "ACCESS_CANCEL", "ERROR_NO_ACTIVATION", "NO_ACTIVATION", "BANNED"]):
                    print(f"{rainbow_otp()} {red}CANCELED{reset}")
                    running = False
                    time.sleep(1)
                    break

                elif status_text.startswith("STATUS_WAIT_RETRY"):
                    # tunggu resend tanpa spam print
                    previous_status = "WAIT_RETRY"

                elif status_text and status_text != previous_status:
                    print(f"{rainbow_otp()} {status_text}")
                    previous_status = status_text

                time.sleep(2)

    main_thread = threading.Thread(target=main_loop)
    main_thread.start()
    main_thread.join(timeout=1)
    
    if auto_cancelled:
        main_thread.join()  # tunggu selesai total
        return
    
    # Tambahan delay pengecekan flag agar memberi waktu main_loop set flag
    for _ in range(3):  # maksimal 3x tunggu
        if auto_cancelled:
            print(f"{rainbow_auto()} Nomor dibatalkan otomatis.")
            return
        time.sleep(0.5)
    
    # Jika user ingin hentikan farming manual (Ctrl+C)
    try:
        input("")  # tekan Enter untuk stop manual
        running = False
    
        if current_activation_id:
            if otp_received_count > 0:
                success_nomor(api, current_activation_id)
            else:
                pass
                t = threading.Thread(
                    target=delayed_cancel,
                    args=(api, current_activation_id, nomor, 120)
                )
                t.daemon = True
                t.start()
                
    except KeyboardInterrupt:
        print(f"{rainbow_warn()} Farming dihentikan oleh user (Ctrl+C).")
    except Exception as e:
        debug_print(f"{rainbow_warn()} Gagal set status nomor manual: {e}")

# ========== MAIN ==========
def main():
    farm_tool()

if __name__ == "__main__":
    main()