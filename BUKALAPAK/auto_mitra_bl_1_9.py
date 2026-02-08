# auto_mitra_bl_1_7.py
# Flow:
# - Jika bukalapak_cookies.json TIDAK ADA/invalid → minta input 1 baris cookie → simpan → lanjut refresh
# - Jika ADA → langsung pakai untuk ambil x_token → ambil access_token (Bearer)
# - Simpan bearer ke: mitra_bearer.json, mitra_bearer.txt, dan .farming
# - Cetak expiry ringkas (WIB)

import os, json, re, time, base64, requests
from datetime import datetime, timezone, timedelta
from colorama import Fore, Style, init

        
# ================== Konstanta ==================
BUKALAPAK_COOKIE_FILE = "bukalapak_cookies.json"
MITRA_BEARER_JSON     = "mitra_bearer.json"
MITRA_BEARER_TXT      = "mitra_bearer.txt"
FARMING_FILE          = ".farming"

WIB = timezone(timedelta(hours=7))

BL_EWALLET_URL  = "https://www.bukalapak.com/servermitra/e-wallet?referrer=widget"
VENDOR_URL_TMPL = "https://app.servermitra.com/vendor/e-wallet?x_token={x}"

UA = (
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36"
)

# ================ Prefix warna/custom =================
# (samakan dengan gaya Farming: [INFO]/[WARN]/[EROR])
def rainbow_info():
        return (Fore.RED + "[" + Fore.YELLOW + "I" + Fore.GREEN + "N" + Fore.CYAN + "F" + Fore.MAGENTA + "O" + Fore.RED + "]" + Fore.RESET)

def rainbow_error():
        return (Fore.RED + "[" + Fore.YELLOW + "E" + Fore.GREEN + "R" + Fore.CYAN + "O" + Fore.MAGENTA + "R" + Fore.RED + "]" + Fore.RESET)

def rainbow_warn():
        return (Fore.RED + "[" + Fore.YELLOW + "W" + Fore.GREEN + "A" + Fore.CYAN + "R" + Fore.MAGENTA + "N" + Fore.RED + "]" + Fore.RESET)

# ================== Util cookies ==================
def parse_cookie_string(cookie_str: str) -> dict:
    """
    Terima 1 baris cookie (format DevTools/HttpCanary):
      name1=val1; name2=val2; ...
    Return dict {name: value}
    """
    jar = {}
    for part in cookie_str.split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        # skip atribut non-cookie
        if k.lower() in {"path","domain","expires","max-age","secure","httponly","samesite","priority"}:
            continue
        jar[k.strip()] = v.strip()
    return jar

def _load_cookies_file(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    try:
        data = json.load(open(path, "r", encoding="utf-8"))
        return data if isinstance(data, dict) and data else None
    except Exception:
        return None

def load_or_prompt_cookies(path: str = BUKALAPAK_COOKIE_FILE) -> dict:
    """
    - Jika file cookies ada & valid → return dict cookies
    - Jika tidak ada / rusak → minta input 1 baris → simpan → return dict cookies
    """
    cookies = _load_cookies_file(path)
    if cookies:
        return cookies

    # tidak ada/invalid → minta input
    print(f"{rainbow_warn()} Cookie Bukalapak belum ada.")
    cookie_str = input("🔐 Input Cookies baru : ").strip()
    cookies = parse_cookie_string(cookie_str)
    if not cookies:
        print(f"{rainbow_error()} Format cookies tidak valid. Harus 'name=value; name2=value2; ...'")
        raise SystemExit(1)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2, ensure_ascii=False)
    print(f"\n{rainbow_info()} Cookies disimpan ke {path}")
    return cookies

def session_with_bukalapak_cookies(cookies: dict) -> requests.Session:
    s = requests.Session()
    # set cookies ke sesi (domain bukalapak)
    for k, v in cookies.items():
        s.cookies.set(k, v, domain=".bukalapak.com")
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.bukalapak.com/",
    })
    return s

# ================== JWT / Expiry ==================
def jwt_decode_noverify(token: str) -> dict:
    """Decode payload JWT tanpa verifikasi (untuk baca iat/exp)."""
    try:
        payload_b64 = token.split(".")[1]
        payload_b64 += "=" * (-len(payload_b64) % 4)  # pad base64
        return json.loads(base64.urlsafe_b64decode(payload_b64))
    except Exception:
        return {}

def _fmt_delta(seconds: int) -> str:
    s = abs(int(seconds))
    jam, sisa = divmod(s, 3600)
    menit, _ = divmod(sisa, 60)
    if jam and menit: return f"{jam} jam {menit} menit"
    if jam:           return f"{jam} jam"
    if menit:         return f"{menit} menit"
    return "kurang dari 1 menit"


# ================== Core flow (x_token → access_token) ==================
def extract_x_token_from_location(location_url: str) -> str | None:
    # location: https://app.servermitra.com/vendor/e-wallet?x_token=eyJ...
    m = re.search(r"[?&]x_token=([^&]+)", location_url)
    return m.group(1) if m else None

def get_x_token(sess: requests.Session) -> str:
    r = sess.get(BL_EWALLET_URL, allow_redirects=False, timeout=30)
    if r.status_code in (301, 302, 303, 307, 308):
        loc = r.headers.get("Location", "")
        xt = extract_x_token_from_location(loc)
        if xt:
            return xt
    # fallback: kadang 200 dengan meta refresh di body
    if r.status_code == 200 and r.text:
        m = re.search(r'url=(https://app\.servermitra\.com/vendor/e-wallet\?x_token=[^"]+)', r.text, re.I)
        if m:
            xt = extract_x_token_from_location(m.group(1))
            if xt:
                return xt
    raise RuntimeError(f"Gagal ambil x_token (status {r.status_code})")

def get_access_token_from_servermitra(x_token: str) -> str:
    url = VENDOR_URL_TMPL.format(x=x_token)
    r = requests.get(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": "https://www.bukalapak.com/",
        },
        timeout=30
    )
    # access_token biasanya di Set-Cookie: access_token=...
    set_cookie = r.headers.get("Set-Cookie", "")
    m = re.search(r"access_token=([^;]+)", set_cookie)
    if not m:
        # edge-case: kadang muncul di body
        m = re.search(r"access_token=([A-Za-z0-9._-]+)", r.text)
    if not m:
        raise RuntimeError("Set-Cookie access_token tidak ditemukan.")
    return m.group(1)

# ================== Save bearer ==================
def save_bearer_files(access_token: str):
    data = {"access_token": access_token, "saved_at": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S %Z")}
    with open(MITRA_BEARER_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    with open(MITRA_BEARER_TXT, "w", encoding="utf-8") as f:
        f.write(access_token)

def refresh_and_save_to(path: str = FARMING_FILE) -> str:
    """
    Fungsi publik (dipanggil Farming):
    - Pastikan cookies ada (prompt jika belum)
    - Ambil x_token → access_token
    - Simpan bearer ke .farming + file pendukung
    - Return token
    """
    cookies = load_or_prompt_cookies()
    sess = session_with_bukalapak_cookies(cookies)

    x_token = get_x_token(sess)
    access_token = get_access_token_from_servermitra(x_token)

    # save bearer ke file
    with open(path, "w", encoding="utf-8") as f:
        f.write(access_token)
    save_bearer_files(access_token)

    # info expiry ringkas
    payload = jwt_decode_noverify(access_token)
    exp = payload.get("exp")

    return access_token

# ================== CLI standalone ==================
if __name__ == "__main__":
    try:
        # Jalankan refresh & simpan ke .farming (sesuai flow Farming menu 6)
        # Output:
        # - Jika cookies tidak ada: prompt → [INFO] Cookies disimpan ke ...
        # - Selanjutnya: [INFO] Token ServerMitra di-refresh otomatis (ini bisa dicetak oleh caller/Farming)
        #                 [INFO] Token disimpan ke .farming ✅ (oleh caller)
        #                 [INFO] Expired: ... WIB (± ... lagi)
        tok = refresh_and_save_to(FARMING_FILE)
        
    except Exception as e:
        print(f"{rainbow_error()} {e}")
        raise SystemExit(1)