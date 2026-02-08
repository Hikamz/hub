import requests, time, sys, select, socket, re
from colorama import Fore, Style, init
init(autoreset=True)
import socket
import threading
import platform

if platform.system() == "Windows":
    import msvcrt
else:
    import tty
    import termios


# **** Warna Global ****
green = Fore.GREEN
red = Fore.RED
yellow = Fore.YELLOW
blue = Fore.BLUE
reset = Fore.RESET

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
        
        
def rainbow_country():
    return (
        Fore.RED + "[" +
        Fore.YELLOW + "C" +
        Fore.GREEN + "O" +
        Fore.CYAN + "U" +
        Fore.MAGENTA + "N" +
        Fore.YELLOW + "T" +
        Fore.GREEN + "R" +
        Fore.CYAN + "Y" +
        Fore.RED + " ]" + Fore.RESET
    )

def rainbow_provider():
    return (
        Fore.RED + "[" +
        Fore.YELLOW + "P" +
        Fore.GREEN + "R" +
        Fore.CYAN + "O" +
        Fore.MAGENTA + "V" +
        Fore.YELLOW + "I" +
        Fore.GREEN + "D" +
        Fore.CYAN + "E" +
        Fore.MAGENTA + "R" +
        Fore.RED + "]" + Fore.RESET
    )

def rainbow_nomor_hp():
    return (
        Fore.RED + "[" +
        Fore.YELLOW + "N" +
        Fore.GREEN + "O" +
        Fore.CYAN + "M" +
        Fore.MAGENTA + "O" +
        Fore.YELLOW + "R" +
        Fore.GREEN + " " +
        Fore.CYAN + "H" +
        Fore.MAGENTA + "P" +
        Fore.RED + "]" + Fore.RESET
    )

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
        print(f"{rainbow_otp()} Nomor {green}{number}{reset} {red}dibatalkan{reset}")
    except Exception as e:
        print(f"{rainbow_otp()} Gagal membatalkan nomor {number}: {e}")  

# ========== API CLIENT LITENSI ==========
class SmsBowerAPI:
    BASE_URL = "https://smsbower.online/stubs/handler_api.php"
    
    def __init__(self, api_id: int, api_key: str):
        self.api_id = api_id
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
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.text.strip()
                
        
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
    

# ========== UI & WRAPPER ==========
def print_otp_ascii():
    print(Fore.GREEN + '''
8""""8 8""""8   8"""88 8   8  8 8"""" 8"""8  
8      8    8   8    8 8   8  8 8     8   8  
8eeeee 8eeee8ee 8    8 8e  8  8 8eeee 8eee8e 
    88 88     8 8    8 88  8  8 88    88   8 
e   88 88     8 8    8 88  8  8 88    88   8 
8eee88 88eeeee8 8eeee8 88ee8ee8 88eee 88   8 
                                             
''' + Style.RESET_ALL)

def layanan_smsbower_map(api: 'SmsBowerAPI'):
    return {
        '1': ('Gojek', 'ni'),
        '2': ('Blibli', 'fk'),
        '3': ('Dana', 'fr'),
        '4': ('Grab', 'jg'),
        '5': ('Lazada', 'dl'),
        '6': ('Tokopedia', 'xd'),
        '7': ('Qpon', 'bnu'),
        '8': ('Ovo', 'xh'),
    }

def pilih_service(api: 'LitensiAPI'):
    m = layanan_smsbower_map(api)
    layanan_text = "LAYANAN OTP"
    rainbow_colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.LIGHTRED_EX]
    rainbow_title = "".join([rainbow_colors[i % len(rainbow_colors)] + c for i, c in enumerate(layanan_text)]) + Style.RESET_ALL
    print(rainbow_title + " :\n")
    for k, (label, sid) in m.items():
        postfix = "" if sid else " (ID not set)"
        print(f"{k}. {label}{postfix}")

    while True:
        p = input(Fore.YELLOW + "\nPilih / Back [b]: " + Style.RESET_ALL).strip().lower()
        if p == "b": 
            return None, None
        if p in m:
            return m[p]
        print(Fore.RED + "Pilihan tidak valid." + Style.RESET_ALL)

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
    teks = "\nPILIH PROVIDER :\n"
    print()
    for i, char in enumerate(teks):
        warna = rainbow[i % len(rainbow)]
        print(warna + char, end='')
    print(Style.RESET_ALL)

    mapping = {}
    for idx, (pid, info) in enumerate(providers.items(), start=1):
        price = info.get("price")
        count = info.get("count")
        print(f"{idx}. {pid} | 💲 {price} | 📦 {count}")
        mapping[str(idx)] = pid  # mapping pilihan ke providerId

    while True:
        pilihan = input(Fore.YELLOW + "\nPilih / Back [b]: " + Style.RESET_ALL).strip().lower()
        if pilihan == "b":
            return "b"
        if pilihan in mapping:
            return mapping[pilihan]
        print(Fore.RED + "Pilihan tidak valid." + Style.RESET_ALL)

def extract_otp_from_text(text):
    # Cari pola umum OTP: bisa "kode OTP", "OTP:", "kode" dst
    match = re.search(r'(?:kode OTP|OTP|kode)\D*(\d{4,6})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    # fallback: ambil 4–6 digit terakhir dari pesan
    fallback = re.findall(r'\b\d{4,6}\b', text)
    if fallback:
        return fallback[-1]
    return None


# ========== FLOW PROSES OTP ==========
def ask_int(prompt, default=0):
    while True:
        try:
            val = input(Fore.YELLOW + f"{prompt} [{default}]: " + Style.RESET_ALL).strip()
            if val == "":
                return default
            return int(val)
        except ValueError:
            print(Fore.RED + "Input harus angka!" + Style.RESET_ALL)


def tunggu_koneksi(pesan_khusus=""):
    print(f"{rainbow_error()} Koneksi terputus. Menunggu koneksi kembali...")
    while True:
        try:
            # Coba bikin koneksi ke DNS Google
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            print(f"{rainbow_info()} Koneksi aman Kembali boss...")
            time.sleep(2)
            if pesan_khusus:
                print(Fore.CYAN + pesan_khusus + Style.RESET_ALL)
            return
        except OSError:
            time.sleep(3)
            
def proses_beli_otp(api: 'SmsBowerAPI', api_key: str, service_id: str, provider_id: str, service_label: str):
    country_code = 6
    country_name = "Indonesia"

    balance_fmt = f"{get_balance(api):.4f}"  # saldo sudah float

    print(Fore.GREEN + f"\n-------------------------------------")
    print(Fore.GREEN + f"SMSBower  | OTP {service_label}")
    print(Fore.GREEN + f"Balance   | {balance_fmt}")
    print(Fore.LIGHTBLACK_EX + f"[Tekan ENTER untuk Batal / Kembali]\n")

    # input target dan batas percobaan
    target_sukses = ask_int("Target OTP sukses", 1)
    batas_percobaan = ask_int("Batas percobaan (0=tak dibatasi)", 0)

    sukses_count = 0
    percobaan_count = 0

    while True:
        if target_sukses and sukses_count >= target_sukses:
            input("\n[ENTER] Target OTP sukses terpenuhi → kembali ke provider...")
            return

        if batas_percobaan and percobaan_count >= batas_percobaan:
            input("\n[ENTER] Batas percobaan tercapai → kembali ke provider...")
            return

        percobaan_count += 1
        print(Fore.GREEN + f"\n--- Order ke-{percobaan_count} (Sukses: {sukses_count}/{target_sukses}) ---")

        # window singkat: ENTER = batal sebelum order
        start_time = time.time()
        while time.time() - start_time < 1.5:
            if key_pressed():
                print(Fore.RED + "\nDibatalkan oleh pengguna. Kembali ke provider." + Style.RESET_ALL)
                return

        # --- Beli nomor ---
        try:
            order = api.create_order(country_code, service_id, provider_ids=provider_id)
        except Exception as e:
            print(Fore.RED + f"❌ Gagal create order: {e}" + Style.RESET_ALL)
            continue

        if "error" in order:
            print(Fore.RED + f"❌ Order gagal: {order['error']}" + Style.RESET_ALL)
            continue

        activation_id = order["activationId"]
        number = order["phoneNumber"]

        print(f"{rainbow_country()} {country_name}")
        print(f"{rainbow_provider()} {provider_id}")
        print(f"{rainbow_nomor_hp()} {Fore.GREEN}{number}{Style.RESET_ALL}")
        print(Fore.GREEN + f"-------------------------------------\n")
        # --- Polling OTP ---
        otp_count_on_this_number = 0
        previous_status = ""
        ended_by_enter = False
        last_otp = None
        same_otp_count = 0

        while True:
            try:
                status = api.get_status(activation_id)

                # Cek input ENTER → DONE/CANCEL
                if key_pressed():
                    ended_by_enter = True
                    if otp_count_on_this_number > 0:
                        api.set_status(activation_id, "SUCCESS")
                        print(f"{rainbow_otp()} {green}DONE{reset}")
                        sukses_count += 1
                    else:
                        print(f"{rainbow_otp()} {red}CANCELED{reset} (setelah 120s)")
                        threading.Thread(
                            target=delayed_cancel,
                            args=(api, activation_id, number, 120),
                            daemon=True
                        ).start()
                    break
    
                if status == "STATUS_WAIT_CODE":
                    if previous_status != "WAITING":
                        print(f"{rainbow_otp()} {yellow}WAITING{reset}")
                        previous_status = "WAITING"

                elif status.startswith("STATUS_OK:"):
                    otp_count_on_this_number += 1
                    code = status.split(":", 1)[1].strip()
                    parsed_otp = extract_otp_from_text(code)
                    
                    otp_text = parsed_otp or code
                    
                    # ==== CEK OTP SAMA TERUS / ORDER SUDAH HABIS ====
                    if otp_text == last_otp:
                        same_otp_count += 1
                
                        if same_otp_count >= 3:
                            print(f"{rainbow_otp()} {red}CANCELED{reset}")
                            try:
                                api.set_status(activation_id, "CANCEL")
                            except:
                                pass
                            break
                
                        time.sleep(1)
                        continue
                    else:
                        last_otp = otp_text
                        same_otp_count = 0
                            
                    if parsed_otp:
                        print(f"{rainbow_otp()} {Fore.GREEN}{parsed_otp}{Style.RESET_ALL}")
                    else:
                        print(f"{rainbow_otp()} {Fore.YELLOW}{code}{Style.RESET_ALL}")
                
                    api.set_status(activation_id, "RETRY")
                    print(f"{rainbow_otp()} {yellow}SUCCESS_RESEND{reset}")
                    previous_status = ""
                
                elif status in ("STATUS_CANCEL", "NO_ACTIVATION"):
                    print(f"{rainbow_otp()} {red}CANCELED{reset}")
                    break
                
                elif status.startswith("STATUS_WAIT_RETRY"):
                    # jangan diprint → biar diam aja sambil nunggu resend
                    previous_status = "WAIT_RETRY"
                
                else:
                    if status and status != previous_status:
                        print(f"{rainbow_otp()} {status}")
                        previous_status = status

            except requests.exceptions.RequestException:
                tunggu_koneksi(f"{rainbow_otp()} Melanjutkan polling status OTP...")

            time.sleep(3)  # jeda polling 3 detik

        # ====== SELESAI 1 NOMOR → DECISION LANJUT / BALIK ======
        if ended_by_enter and target_sukses and sukses_count >= target_sukses:
            input("\n[ENTER] Target terpenuhi → kembali ke provider...")
            return
        else:
            lanjut = input("\n[ENTER] lanjut... / [b] kembali ke provider: ").strip().lower()
            if lanjut == 'b':
                return
            # ENTER → loop lanjut beli nomor berikutnya

def loop_provider(api: 'SmsBowerAPI', api_key: str, service_id: str, service_label: str):
    """
    Loop pemilihan provider berdasarkan hasil getPricesV3,
    lalu masuk ke proses_beli_otp untuk setiap provider yang dipilih.
    """
    while True:
        provider_id = load_provider_list(api_key, service_id, 6)
        if provider_id == "b":
            print()
            return "back_to_service"
        if not provider_id:
            print(f"{rainbow_otp()} Provider tidak valid.")
            return None

        # Masuk ke proses beli OTP dengan provider yang dipilih
        proses_beli_otp(api, api_key, service_id, provider_id, service_label)
        
# ========== MAIN ==========
def main():
    api_key = load_smsbower_cred()
    if not api_key:
        return

    api = SmsBowerAPI(api_id=0, api_key=api_key)
    print_otp_ascii()
    
    while True:
        label, service_id = pilih_service(api)
        if not service_id:
            print("Kembali ke menu utama.")
            return

        result = loop_provider(api, api_key, service_id, label)
        if result == "back_to_service":
            # user pilih back di menu provider → ulang ke menu layanan OTP
            continue
        else:
            break

if __name__ == "__main__":
    main()