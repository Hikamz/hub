#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GpyGames – Menu Checkout Otomatis (v2.1)
- UI diringkas: sembunyikan detail STEP 1–3 (tampilkan error saja)
- Output terminal ala "moba style" + simpan ke CSV & TXT (link payment)
- Tidak mengubah fungsi/f low inti selain tampilan & logging

Berbasis GpyGames1.13.py pengguna.
"""

import json, re, time, sys
from typing import Any, Dict, List, Tuple, Optional
import requests
import os
import csv
from datetime import datetime
from colorama import Fore, Style, init
import glob
import inspect
from concurrent.futures import ThreadPoolExecutor, as_completed

DEBUG_MODE = True
def debug_print(*args, **kwargs):
    if DEBUG_MODE:
        print("[DEBUG]", *args, **kwargs)
 
 # **** Warna Global ****
green = Fore.GREEN
red = Fore.RED
yellow = Fore.YELLOW
blue = Fore.BLUE
reset = Fore.RESET

def ts():
    """Buat timestamp jam:menit:detik untuk debug"""
    return time.strftime("%H:%M:%S")
    
BASE = "https://gopay.co.id/games/v1"
PRODUCT_SLUG = "mobile-legends-bang-bang"

# ====== SESSION & DEFAULT HEADERS ======
s = requests.Session()
HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36"
    ),
    "Accept-Encoding": "gzip, deflate",
    "accept": "*/*",
    "Connection": "keep-alive",
    "content-type": "application/json",
    "x-client": "mobile",
    "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "origin": "https://gopay.co.id",
    "referer": f"https://gopay.co.id/games/{PRODUCT_SLUG}",
}
COOKIES = {}
s.headers.update(HEADERS)
s.cookies.update(COOKIES)

# ====== CONFIG: MENU/FILTER ======
PROMO_ONLY = True
MOBILE_PRICE_ONLY = True

def ff_short_filter(items):
    """Ambil hanya denom kecil FF (5,10,20,50,70,100,140); buang member/BP/weekly/voucher."""
    allowed = {5, 10, 20, 50, 70, 100, 140}
    out = []
    for it in items:
        name = (it.get("name") or "").strip().lower()
        # buang paket non-denom
        if any(bad in name for bad in ("member", "bp", "weekly", "bulanan", "voucher")):
            continue
        # ambil angka di awal, pastikan benar-benar denom (bukan 355/425, dll)
        m = re.match(r"^\s*(\d+)\s*diamonds?\b", name)
        if not m:
            continue
        if int(m.group(1)) in allowed:
            out.append(it)
    return out
    
def mlbb_short_filter(items):
    """
    Ambil hanya:
      - Weekly Diamond Pass (pilih yang termurah)
      - 3, 5, 44, 59 Diamonds (persis denomnya; buang paket lain)
    """
    import re

    allowed_denoms = {3, 5, 44, 59}
    out = []

    # -- Weekly Diamond Pass: pilih yang termurah saja
    wdp = [it for it in items if "weekly" in (it.get("name","").lower())
                           and "diamond pass" in (it.get("name","").lower())]
    if wdp:
        cheapest = min(wdp, key=_price_of)
        out.append(cheapest)

    # -- Denom persis 3/5/44/59 Diamonds (hindari 355, 425, dst)
    for it in items:
        name = (it.get("name") or "").strip().lower()

        # singkirkan paket non-denom
        if any(bad in name for bad in ("member", "bp", "weekly", "bulanan", "voucher")):
            continue

        m = re.match(r"^\s*(\d+)\s*diamonds\b", name)
        if not m:
            continue

        n = int(m.group(1))
        if n in allowed_denoms:
            out.append(it)

    return out
    
GAME_SHORT_MENU = {
    "mlbb": mlbb_short_filter,
    "freefire": ff_short_filter,
    "steam": None,
    "roblox": None
}

# Fungsi untuk memberi warna ANSI
def warna_teks(teks, warna):
    kode_warna = {
        "merah": "\033[31m",
        "kuning": "\033[33m",
        "hijau": "\033[32m",
        "reset": "\033[0m"
    }
    return f"{kode_warna.get(warna, '')}{teks}{kode_warna['reset']}"

# Mapping warna untuk status
STATUS_WARNA = {
    "paid": "hijau",
    "pending": "kuning",
    "expired": "merah",
    "canceled": "merah",
    "error": "merah",
    "unknown": "reset",
}

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _match_keywords(name: str, inc: List[str], exc: List[str]) -> bool:
    n = _norm(name)
    if exc and any(k in n for k in exc):
        return False
    if not inc:
        return True
    return any(k in n for k in inc)

def _price_of(item: dict) -> int:
    for k in ("priceDiscountMobile", "priceDiscount", "price"):
        v = item.get(k)
        if isinstance(v, (int, float)) and v > 0:
            return int(v)
    return 0
    
def _parse_user_zone_list(s: str):
    """
    Terima input seperti:
      "1542261223 16483, 1234567 890"  (dipisah koma)
    atau multi-baris:
      1542261223 16483
      1234567 890
    Kembalikan list of (user_id, zone_id) sebagai string.
    """
    pairs = []
    for part in (s or "").replace(",", "\n").splitlines():
        part = part.strip()
        if not part:
            continue
        toks = part.split()
        if len(toks) < 2:
            print(f"[WARN] Lewati baris tidak valid: {part!r}")
            continue
        uid, zid = toks[0].strip(), toks[1].strip()
        if uid and zid:
            pairs.append((uid, zid))
    return pairs
    
# ===== auto cekout menu 4 =====
def validate_voucher(code: str, amount: int, product_id: int, user_id: str, zone_id: str = "") -> dict:
    url = f"{BASE}/voucher/validate"
    payload = {
        "code": code,
        "amount": amount,
        "productId": product_id,
        "paymentChannelId": 73,
        "data": {"userId": str(user_id), "zoneId": str(zone_id)},
    }
    start = time.time()
    r = batch_session.post(url, headers=HEADERS, json=payload, timeout=BATCH_TIMEOUT)
    debug_print(f"{yellow}⏱️ [validate_voucher] {time.time()-start:.2f}s{reset}")
    return _json_or_raw(r)
    
def wait_until(hour=15, minute=0, second=0):
    while True:
        now = datetime.now()
        if (now.hour > hour) or \
           (now.hour == hour and now.minute > minute) or \
           (now.hour == hour and now.minute == minute and now.second >= second):
            break
        print(f"⏳ Menunggu jam {hour:02d}:{minute:02d}:{second:02d} (sekarang {now.strftime('%H:%M:%S')})")
        time.sleep(0.5)  # cek tiap 0.5 detik biar presisi

def parse_target_time(s: str):
    """Parse string jam HH:MM[:SS] jadi tuple (hour, minute, second)"""
    parts = s.strip().split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    second = int(parts[2]) if len(parts) > 2 else 0
    return hour, minute, second
        
def _append_batch_txt(user_id: str, invoice_id: str, paylink: str, final_amount: int, path: str):
    inv_url = f"https://gopay.co.id/games/payment/{invoice_id}"
    line = (
        f"✅ {user_id} Checkout berhasil.\n"
        f"🧾 Invoice : {inv_url}\n"
        f"🔗 Link Bayar: {paylink}\n"
        f"💰 Harga   : {final_amount}\n\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)
    
        
def run_menu3_batch_details():
    import os, glob
    from datetime import datetime

    # Cari semua file batch .txt
    files = sorted(
        glob.glob("logs/trx-batch-*.txt"),
        key=os.path.getmtime,
        reverse=True,
    )
    if not files:
        print("⚠️  Tidak ada file batch .txt di folder logs/. Jalankan menu 4 dulu.")
        return

    # Tampilkan daftar file
    print("\n📂 Daftar TXT Batch (terbaru → lama):")
    for i, p in enumerate(files, 1):
        dt = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")
        print(f"   {i:>2}. {os.path.basename(p):<25} • {dt} • {_human_size(os.path.getsize(p))}")

    ans = input("\n👉 Pilih file (contoh: 1,3,5). Kosong=terbaru saja: ").strip()

    # Pilih file
    sel_paths = []
    if not ans:
        sel_paths = [files[0]]
    else:
        picks = [x.strip() for x in ans.split(",") if x.strip()]
        for x in picks:
            if x.isdigit() and 1 <= int(x) <= len(files):
                sel_paths.append(files[int(x) - 1])

    if not sel_paths:
        print("⚠️  Pilihan kosong/invalid.")
        return

    cnt = {"paid": 0, "pending": 0, "expired": 0, "canceled": 0, "error": 0, "unknown": 0}
    total = 0

    # Loop tiap file batch
    for path in sel_paths:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()

        # Ambil invoice links
        invoices = [ln.split("Invoice :")[1].strip() for ln in lines if ln.startswith("🧾 Invoice")]
        total += len(invoices)

        for idx, inv_url in enumerate(invoices, 1):
            invoice_id = inv_url.split("/")[-1]  # ambil ID dari URL
            trx = {}
            stat_raw = ""
            try:
                trx = get_transaction(invoice_id)
                stat_raw = trx.get("status") or ""
            except Exception as e:
                stat_raw = f"error: {e}"

            key = _norm_status(stat_raw)
            cnt[key] = cnt.get(key, 0) + 1

            uid = _get(trx, "summary", "summaryProduct", "data", "userId") or "-"
            zid = _get(trx, "summary", "summaryProduct", "data", "zoneId") or ""
            ign = _get(trx, "summary", "summaryProduct", "ign") or "-"
            item = _get(trx, "summary", "summaryProduct", "productItemName") or "-"
            amount = trx.get("totalAmount") or trx.get("amount") or "-"
            payment_name = _get(trx, "summaryPayment", "name") or "-"
            order_no = trx.get("orderNo") or invoice_id
            pay_time = trx.get("createdDate") or trx.get("finishedDate") or trx.get("paidDate") or "-"
            # convert UTC ke WIB
            if pay_time and isinstance(pay_time, str) and pay_time.endswith("Z"):
                try:
                    from datetime import datetime, timedelta
                    dt = datetime.fromisoformat(pay_time.replace("Z", "+00:00"))
                    pay_time = (dt + timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
                  
            # --- Cetak detail ---
            print(f"\n{BOLD}[Status Order] ➜ {idx}/{len(invoices)}{RESET}")
            print(f"🆔 Order ID   : {order_no}")
            print(f"📅 Pay Time   : {pay_time}")
            print(f"🎮 Game ID    : {uid} ({zid})")
            print(f"👤 Username   : {ign}")
            print(f"🎁 Item Name  : {item}")
            print(f"💶 Amount     : Rp{amount}")
            print(f"💳 Payment    : {payment_name}")
            label = END_LABELS.get(key, key.capitalize())
            colored_label = warna_teks(label, STATUS_WARNA.get(key, 'reset'))
            print(f"📌 Status     : {_status_emoji(key)} {colored_label}")

            if idx < len(invoices):
                time.sleep(CHECK_DELAY_S)

    # Ringkasan
    print(
        f"\n📊 Ringkasan :  ✅ {cnt['paid']}  |  ⏳ {cnt['pending']}  |  ❌ {cnt['expired']}  |  🚫 {cnt['canceled']}  |  ⚠️ {cnt['error']}  |  ❓ {cnt['unknown']}"
    )
    input("\n[ENTER] untuk kembali...")
    
# --- Session cepat khusus batch voucher ---
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

batch_session = requests.Session()
retry_policy = Retry(
    total=3,                 # retry max 3x kalau gagal
    backoff_factor=0.5,      # jeda antar retry: 0.5s, 1s, 2s
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST", "GET"]
)
batch_session.mount("https://", HTTPAdapter(max_retries=retry_policy))
batch_session.mount("http://", HTTPAdapter(max_retries=retry_policy))

BATCH_TIMEOUT = 60  # timeout diperpanjang

def process_checkout(uid, zid, kode, picked, game_key, max_retry=1):
    try:
        # === STEP 1: Inquiry sekali untuk lock order_id ===
        INQUIRY_PAYLOAD = build_inquiry_payload_voucher(
            game_key, picked, uid, zid, voucher_code=kode
        )
        debug_print(f"[{ts()}] Inquiry Payload {uid}: {json.dumps(INQUIRY_PAYLOAD, indent=2)}")
        resp_inq = inquiry_safe(INQUIRY_PAYLOAD)
        debug_print(f"[{ts()}] Inquiry Resp {uid}: {resp_inq}")

        msg_inq = (resp_inq.get("message") or resp_inq.get("error") or "").lower()
        
        if "this voucher is not available at this time" in msg_inq:
            return f"⏳ {uid} Kode voucher belum berlaku"

        if str(resp_inq.get("statusCode")) == "404" and "invalid user account" in msg_inq:
            return f"❌ {uid} ID Game INVALID"

        if str(resp_inq.get("statusCode")) == "400":
            if "unavailable" in msg_inq:
                return f"🚫 {uid} Kuota voucher HABIS"
            elif "redeem limit" in msg_inq:
                return f"❌ {uid} ID Game LIMIT"
            else:
                return f"[{uid}] ⚠️ Error Inquiry: {msg_inq}"
                
        order_id = extract_order_id(resp_inq)
        debug_print(f"🔑 {uid} Order ID locked: {order_id}")

        """
        # === STEP 2: Apply voucher ===
        resp = validate_voucher(
            kode,
            amount=_price_of(picked),
            product_id=INQUIRY_PAYLOAD["productId"],
            user_id=uid,
            zone_id=zid,
        )
        
        # tampilkan total restok kalau ada
        if isinstance(resp, dict):
            if "data" in resp and isinstance(resp["data"], dict):
                if "total" in resp["data"]:
                    total = resp["data"]["total"]
                    print(f"{green}📢 Sisa voucher tersedia: {total}{reset}")
            
        debug_print(f"[{ts()}] Voucher Resp {uid}: {resp}")
        msg = resp.get("message") or resp.get("error") or str(resp)
        debug_print(f"[DEBUG] {uid} Voucher message: {msg}")

        if str(resp.get("statusCode")) == "400":
            if "unavailable" in (msg or "").lower():
                return f"❌ {uid} Kuota voucher HABIS"
                
        if str(resp.get("statusCode")) not in ("200", "201") and "valid" not in msg.lower():
            return f"❌ {uid} Voucher gagal: {msg}"

        debug_print(f"✅ {uid} Voucher OK, lanjut checkout...")
        """
        
        # === STEP 3: Loop retry payment (tanpa bikin order baru) ===
        status = "0"
        msg_pay = ""
        for attempt in range(1, max_retry + 1):
            try:
                pay = payment_voucher({
                    "orderId": order_id,
                    "paymentChannelId": 73,
                    "phoneNumber": "628783219212",
                    "paymentPhoneNumber": "",
                    "quantity": 1,
                    "invoiceUrl": "https://gopay.co.id/games/payment/",
                })
                debug_print(f"[{ts()}] Raw Payment Resp {uid} [try {attempt}]: {pay}")
                
                pj = pay.get("json") or {}
                if isinstance(pj, str):
                    try:
                        pj = json.loads(pj)
                    except:
                        pj = {}

                status = str(pay.get("status") or pay.get("statusCode") or "0")

                # Ambil pesan dari root JSON maupun string error
                msg_pay = (
                    (pj.get("message") if isinstance(pj, dict) else "")
                    or (pj.get("error") if isinstance(pj, dict) else "")
                    or pay.get("message")
                    or pay.get("error")
                    or ""
                ).lower()
                
                if status == "400":
                    if "oops" in msg_pay:
                        debug_print(f"[{ts()}] ⚠️ {uid} Oops detected, retry {attempt}/{max_retry}")
                        time.sleep(1)
                        continue
                    elif "Voucher is unavailable" in msg_pay:
                        return f"🚫 {uid} Kuota voucher HABIS"
                    elif "order id is required" in msg_pay:
                        return f"❌ {uid} Payment gagal: Order ID kosong/tidak valid"
                    elif not msg_pay:
                        return f"⚠️ {uid} Payment gagal: Bad Request"
                                                    
                # cari invoice id
                invoice_id = (
                    pay.get("invoiceId")
                    or pay.get("Id")
                    or pj.get("invoiceId")
                    or (pj.get("data") or {}).get("invoiceId")
                    or pj.get("data")  # fallback kadang string MLBBX...
                )

                # Kalau sukses → return berhasil
                if str(status) in ("200", "201") or "success" in msg_pay:
                    inv_url = f"https://gopay.co.id/games/payment/{invoice_id}" if invoice_id else "-"
                    
                    # ambil link deeplinkRedirect & final amount dari transaksi
                    paylink = "-"
                    final_amount = "?"
                    trx = get_transaction(invoice_id)
                    if isinstance(trx, dict):
                        act = trx.get("actionPayment") or {}
                        paylink = act.get("deeplinkRedirect") or act.get("paymentDirect") or "-"
                        final_amount = trx.get("totalAmount") or trx.get("amount") or "?"

                    batch_txt = f"logs/trx-batch-{game_key}-{datetime.now():%Y%m%d}.txt"
                    _append_batch_txt(uid, invoice_id, paylink, final_amount, batch_txt)
                    
                    return (
                        f"✅ {uid} Checkout berhasil.\n"
                        f"🧾 Invoice : {inv_url}\n"
                        f"🔗 Link Bayar: {paylink}\n"
                        f"💰 Harga   : {final_amount}"
                    )

                    batch_txt = f"logs/trx-batch-{game_key}-{datetime.now():%Y%m%d}.txt"
                    _append_batch_txt(uid, invoice_id, paylink, final_amount, batch_txt)
                    
                # Kalau gagal, tunggu retry
                retry_after = 1
                try:
                    hdr = pay.get("headers") or {}
                    retry_after = int(hdr.get("x-retry-after", retry_after))
                except Exception:
                    pass

                debug_print(f"⚠️ {uid} Attempt {attempt} gagal (status {status}), retry {retry_after}s ...")
                time.sleep(retry_after)

            except Exception as e:
                debug_print(f"⚠️ {uid} Error attempt {attempt}: {e}")
                
            if str(status) == "400" and "oops" in msg_pay.lower():
                return f"⚠️ {uid} Payment gagal (Oops) - Order locked tanpa invoice"

    except Exception as e:
        return f"⚠️ {uid} Fatal Error: {e}"
       
def batch_checkout_fast(game_key, ids_file, voc_file=None, start_hour=15, start_minute=0, start_second=0, kode_manual=""):
    # baca file ids
    with open(ids_file, encoding="utf-8") as f:
        ids = [ln.strip() for ln in f if ln.strip()]

    vocs = []
    if voc_file:
        with open(voc_file, encoding="utf-8") as f:
            vocs = [ln.strip() for ln in f if ln.strip()]

    # standby sampai jam target
    wait_until(start_hour, start_minute, start_second)

    prod, items = fetch_items_for(game_key)
    
    # default item per game
    if game_key == "freefire":
        # cari item 100 Diamonds, fallback ke items[0] kalau ga ketemu
        picked = next((it for it in items if "100" in (it.get("name") or "")), items[0])
    else:
        picked = items[0]

    results = []
    with ThreadPoolExecutor(max_workers=len(ids)) as ex:
        futures = []
        for i, line in enumerate(ids):
            parts = line.split()
            uid, zid = parts[0], (parts[1] if len(parts) > 1 else "-")

            if kode_manual:
                kode = kode_manual
            else:
                kode = vocs[i] if i < len(vocs) else ""

            futures.append(ex.submit(process_checkout, uid, zid, kode, picked, game_key))

        for f in as_completed(futures):
            results.append(f.result())

    print("\n📊 Hasil Batch Checkout:")
    for r in results:
        print(r)
    input(f"\nENTER untuk kembali")
        
# ===== Helpers: baca log & normalisasi status =====

def _latest_trx_csv() -> str:
    """Cari file logs/trx-*.csv terbaru."""
    pat = os.path.join(LOG_DIR, "trx-*.csv")
    files = sorted(glob.glob(pat), key=os.path.getmtime, reverse=True)
    return files[0] if files else ""

def _read_trx_rows(path_csv: str):
    """Baca CSV transaksi -> list[dict]."""
    rows = []
    if not path_csv or not os.path.exists(path_csv):
        return rows
    with open(path_csv, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)
    return rows

def _norm_status(s: str) -> str:
    """Map status bebas -> paid/pending/expired/error/unknown."""
    t = (s or "").strip().lower()
    if any(x in t for x in ["success", "paid", "lunas", "sukses"]):
        return "paid"
    if any(x in t for x in ["pending", "unpaid", "created", "belum"]):
        return "pending"
    if any(x in t for x in ["expire", "expired", "timeout"]):
        return "expired"
    if any(x in t for x in ["canceled", "cancelled", "timeout"]):
        return "canceled"
    if any(x in t for x in ["fail", "error", "cancel"]):
        return "error"
    return "unknown"

def _status_emoji(key: str) -> str:
    return {
        "paid": "✅",
        "pending": "⏳",
        "expired": "❌",
        "canceled": "🚫",
        "error": "☣️",
        "unknown": "❓",
    }.get(key, "❓")

def _human_size(n: int) -> str:
    for u in ("B","KB","MB","GB"):
        if n < 1024:
            return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.0f}TB"

def _list_trx_csvs(limit: int = 100) -> list[tuple[str, float, int]]:
    """
    Kembalikan list [(path, mtime, size)] urut terbaru→lama untuk logs/trx-*.csv
    """
    import glob, os, time
    pat = os.path.join(LOG_DIR, "trx-*.csv")
    files = [(p, os.path.getmtime(p), os.path.getsize(p)) for p in glob.glob(pat)]
    files.sort(key=lambda x: x[1], reverse=True)
    return files[:limit]

def _read_many_csv(paths: list[str]) -> list[dict]:
    rows: list[dict] = []
    for p in paths:
        rows.extend(_read_trx_rows(p))
    return rows
    
def _extract_invoice_id(row: dict) -> str | None:
    inv = (row.get("invoiceId") or "").strip()
    if inv:
        return inv
    url = (row.get("invoiceUrl") or "").strip()
    if "/games/payment/" in url:
        return url.rsplit("/", 1)[-1]
    return None

def _get(d, *path, default=None):
    cur = d or {}
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default

def _extract_ign_from_sn(sn: str | None):
    if not sn:
        return None
    m = re.search(r'IGN[:\s]+(.+?)(?:\s+Ref:|$)', sn, re.IGNORECASE)
    return m.group(1).strip() if m else None
    
# Label human‑readable untuk status akhir
END_LABELS = {
    "paid": "Success",
    "pending": "Pending",
    "expired": "Expired",
    "canceled": "Canceled",
    "error": "Error",
    "unknown": "-",
}

def run_menu2_summary():
    # === PILIH CSV seperti menu 3 ===
    from glob import glob
    import os
    from datetime import datetime
    
    files = sorted(glob("logs/trx-*.csv"), key=os.path.getmtime, reverse=True)
    if not files:
        print("Tidak ada file CSV di folder logs/.")
        input("[ENTER] untuk kembali...")
        return
    
    print("\n📂 Daftar CSV (terbaru → lama):")
    for i, p in enumerate(files, 1):
        t = datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")
        sz = os.path.getsize(p)
        print(f"  {i}. {os.path.basename(p)} • {t} • {sz}B")
    
    sel = input("\n🔎 Pilih file (contoh 1,3,5). Kosong=terbaru saja: ").strip()
    if sel == "":
        csv_path = files[0]
    else:
        try:
            idx = int(sel) - 1
            csv_path = files[idx]
        except Exception:
            print("Input tidak valid.")
            input("[ENTER] untuk kembali...")
            return
    
    # === jalankan ringkasan utk csv_path terpilih ===
    src = csv_path
    
    # kalau user hanya ketik nama file, coba resolve ke folder logs/
    if src and not os.path.exists(src):
        guess = os.path.join(LOG_DIR, src)
        if os.path.exists(guess):
            src = guess
    
    if not src or not os.path.exists(src):
        print("⚠️  CSV tidak ditemukan.")
        return

    rows = _read_trx_rows(src)
    if not rows:
        print("⚠️  CSV kosong.")
        return

    print("\n🧾 Ringkasan :\n" + "—" * 60)
    cnt = {"paid": 0, "pending": 0, "expired": 0, "error": 0, "unknown": 0}
    checked_rows = []

    for i, row in enumerate(rows, 1):
        inv = row.get("invoiceId") or row.get("orderId") or "-"
        amount = row.get("amount") or row.get("price") or "0"
        # Ambil status terbaru via get_transaction
        stat_raw = ""
        try:
            trx = get_transaction(inv)
            if isinstance(trx, dict):
                stat_raw = trx.get("status") or ""
        except Exception as e:
            stat_raw = f"error: {e}"

        key = _norm_status(stat_raw or row.get("status") or "")
        cnt[key] = cnt.get(key, 0) + 1

        # Warna status
        label = stat_raw or "-"
        if any(k in label for k in ["Belum", "Pending"]):
            label = "Pending"
        elif "Lunas" in label or "Sukses" in label:
            label = "Success"
        elif "Expired" in label:
            label = "Expired"
        
        if label == "Expired":
            stat_warna = f"\033[31m{label}\033[0m"   # merah
        elif label == "Pending":
            stat_warna = f"\033[33m{label}\033[0m"   # kuning
        elif label == "Success":
            stat_warna = f"\033[32m{label}\033[0m"   # hijau
        else:
            stat_warna = label
        
        print(f"{i:>2}. {_status_emoji(key)} {inv:<25} • {stat_warna:<12} • {amount}")

        # siapkan row checked utk disimpan
        cr = dict(row)
        cr["statusChecked"] = stat_raw or row.get("status") or ""
        checked_rows.append(cr)

    print("—" * 60)
    print(f"✅ Lunas   : {cnt['paid']}")
    print(f"⏳ Pending : {cnt['pending']}")
    print(f"❌ Expired : {cnt['expired']}")
    if cnt["error"]:
        print(f"⚠️ Error : {cnt['error']}")
    if cnt["unknown"]:
        print(f"❓ Unknown : {cnt['unknown']}")


def _get(d, *path, default=None):
    cur = d or {}
    for k in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return cur if cur is not None else default
    
CHECK_DELAY_S = 1  # jeda antar get_transaction di Menu 3
def run_menu3_details():
    import os
    # List semua CSV transaksi
    files = _list_trx_csvs()
    if not files:
        print("⚠️  Tidak ada file CSV di folder logs/. Jalankan menu 1 dulu.")
        return

    # Tampilkan daftar (D0=D1=opsi hapus)
    print("\n📂 Daftar CSV (terbaru → lama):")
    for i, (p, m, sz) in enumerate(files):
        dt = datetime.fromtimestamp(m).strftime("%Y-%m-%d %H:%M:%S")
        print(f"   {i+1:>2}. {os.path.basename(p):<20} • {dt} • {_human_size(sz)}")

    print("\n👉 Pilih file (contoh: 1,3,5). Kosong=terbaru saja.")
    print("👉 Ketik D1,D3 untuk HAPUS file 1 & 3 (opsional).")
    ans = input("🪫 ").strip()

    # Mode hapus
    if ans.upper().startswith("D"):
        to_del = [x.strip().lstrip("Dd") for x in ans.split(",") if x.strip()]
        idxs = []
        for x in to_del:
            if x.isdigit() and 1 <= int(x) <= len(files):
                idxs.append(int(x)-1)
        if not idxs:
            print("⚠️  Tidak ada indeks valid untuk dihapus.")
            return
        print("🗑  Konfirmasi hapus:")
        for i in idxs:
            print("   -", os.path.basename(files[i][0]))
        ok = input("Ketik 'YES' untuk lanjut: ").strip().upper()
        if ok == "YES":
            import os
            for i in sorted(idxs, reverse=True):
                try:
                    os.remove(files[i][0])
                    print("   ✔️  Hapus:", os.path.basename(files[i][0]))
                except Exception as e:
                    print("   ❌  Gagal:", files[i][0], "-", e)
        return

    # Pilih file untuk dibaca
    sel_paths: list[str] = []
    if not ans:
        sel_paths = [files[0][0]]
    else:
        picks = [x.strip() for x in ans.split(",") if x.strip()]
        for x in picks:
            if x.isdigit() and 1 <= int(x) <= len(files):
                sel_paths.append(files[int(x)-1][0])
    if not sel_paths:
        print("⚠️  Pilihan kosong/invalid.")
        return

    # Gabungkan semua baris dari banyak CSV
    rows = _read_many_csv(sel_paths)
    if not rows:
        print("⚠️  CSV terpilih kosong.")
        return

    total = len(rows)
    cnt = {"paid": 0, "pending": 0, "expired": 0, "error": 0, "unknown": 0}

    for i, row in enumerate(rows, 1):
        inv = row.get("invoiceId") or row.get("Id") or row.get("orderId") or "-"
        amt = row.get("amount") or row.get("price") or "0"
        uid = row.get("userId") or "-"
        zid = row.get("zoneId") or "-"
        item = row.get("itemName") or "-"
        when = row.get("ts") or "-"

        stat_raw = ""
        order_no = inv
        pay_time = when
        trx = {}
        try:
            trx = get_transaction(inv)
            if isinstance(trx, dict):
                stat_raw = trx.get("status") or ""
                order_no = trx.get("orderNo") or trx.get("orderId") or order_no
                pay_time = trx.get("paymentTime") or trx.get("createdAt") or when
        except Exception as e:
            stat_raw = f"error: {e}"

        # ambil IGN (username) dari summary
        ign = (
            _get(trx, "summary", "summaryProduct", "ign")
            or _get(trx, "summaryProduct", "ign")
            or _extract_ign_from_sn(trx.get("sn"))
            or row.get("username")
            or "-"
        )
        
        # ambil nama payment dari summaryPayment, atau fallback 'payment.name'
        payment_name = (
            _get(trx, "summary", "summaryPayment", "name")
            or _get(trx, "summaryPayment", "name")
            or _get(trx, "payment", "name")
            or row.get("payment")
            or "-"
        )

        # ambil SN (serial number / kode voucher)
        sn_code = (
            trx.get("sn")
            or _get(trx, "summary", "sn")
            or row.get("sn")
            or "-"
        )
        
        key = _norm_status(stat_raw or row.get("status") or "")
        cnt[key] = cnt.get(key, 0) + 1
        username = row.get("ign") or "-"
        
        # --- cetak Game ID ---
        if str(uid).upper() == "VOUCHER":
            # Mode Steam: userId = VOUCHER → gabung dengan SN
            game_id_str = f"{uid} ({sn_code})"
        else:
            # Mode MLBB / FF: gabung userId + zoneId biasa
            game_id_str = f"{uid} ({zid or ''})"
        
        print(f"\n{BOLD}[Status Order] ➜ {i}/{total}{RESET}")
        print(f"🆔 Order ID  : {order_no}")
        print(f"📅 Pay Time  : {row.get('ts') or _get(trx, 'finishedDate') or '-'}")
        print(f"🎮 Game ID   : {game_id_str}")
        print(f"👤 Username  : {ign}")
        print(f"🎁 Item Name : {item}")
        print(f"💶 Amount    : {amt}")
        print(f"💳 Payment   : {payment_name}")
        label = END_LABELS.get(key, key.capitalize())
        colored_label = warna_teks(label, STATUS_WARNA.get(key, "reset"))
        print(f"🧬️ Status    : {_status_emoji(key)} {colored_label}")
       # ... cetak detail status order seperti biasa
        # jeda kecil agar tidak nembak semua sekaligus
        if i < total:
            time.sleep(CHECK_DELAY_S)
            
    print(f"\n📊 Ringkasan :  ✅ {cnt['paid']}  |  ⏳ {cnt['pending']}  |  ❌ {cnt['expired']}  |  ⚠️ {cnt['error']}  |  ❓ {cnt['unknown']}")
    input("\n[ENTER] untuk lanjut...")
    
# ====== HTTP HELPERS ======
def _json_or_raw(r: requests.Response):
    try:
        return r.json()
    except Exception:
        return r.text

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_CSV = os.path.join(LOG_DIR, datetime.now().strftime("trx-%Y%m%d.csv"))
LOG_LINKS = os.path.join(LOG_DIR, datetime.now().strftime("link_pay-%Y%m%d.txt"))

# --- Per-game log paths ---
def _log_paths_for(game_key: str) -> tuple[str, str]:
    """
    Kembalikan (path_csv, path_txt) berdasarkan game.
    Contoh:
      trx-mlbb-20250814.csv
      pay_mlbb_140825.txt
    """
    tag = {"mlbb": "mlbb", "freefire": "ff", "steam": "steam", "roblox": "rbx"}.get(game_key, "misc")
    csv_path = os.path.join(LOG_DIR, datetime.now().strftime(f"trx-{tag}-%Y%m%d.csv"))
    txt_path = os.path.join(LOG_DIR, datetime.now().strftime(f"pay_{tag}_%d%m%y.txt"))
    return csv_path, txt_path

def _append_csv(row: dict, path: str | None = None):
    """Append satu baris ke CSV per-game; auto-header kalau file baru."""
    field_order = [
        "ts","userId","zoneId","productId","productItemId","itemName","price",
        "orderId","invoiceId","status","amount","deeplink","invoiceUrl"
    ]
    target = path or LOG_CSV
    new_file = not os.path.exists(target)
    with open(target, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=field_order)
        if new_file:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in field_order})

def _append_paylink(user_id: str, zone_id: str, item_name: str,
                    invoice_id: str, link: str, path: str | None = None):
    ts = datetime.now().strftime("[%H:%M:%S]")
    line = f"{ts} {user_id} {zone_id} | {item_name} | {invoice_id} | {link}\n"
    target = path or LOG_LINKS
    with open(target, "a", encoding="utf-8") as f:
        f.write(line)

def _dump_json(name: str, data):
    """Opsional: simpan raw JSON untuk debug per invoice."""
    try:
        import json
        fname = os.path.join(LOG_DIR, f"{name}-{datetime.now().strftime('%H%M%S.%f')}.json")
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def call_prepare(game_key: str, payload: dict) -> dict:
    prof = GAMES[game_key]
    uid = str((payload.get("data") or {}).get("userId") or "")
    zid = str((payload.get("data") or {}).get("zoneId") or "")
    return prepare_slug(prof["slug"], uid, zid if prof["need_zone"] else "")

def extract_order_id(resp):
    """
    Ambil orderId dari berbagai bentuk respons.
    Coba di root, lalu di data, dan fallback orderNo.
    """
    def _g(d, *keys, default=None):
        cur = d
        for k in keys:
            if not isinstance(cur, dict): return default
            cur = cur.get(k)
        return cur if cur is not None else default

    if not isinstance(resp, dict):
        return None

    return (
        _g(resp, "orderId")
        or _g(resp, "data", "orderId")
        or _g(resp, "orderNo")
        or _g(resp, "data", "orderNo")
    )
    
# --- PRODUCT HELPERS ---
def get_product(slug: str) -> dict:
    """
    Ambil detail katalog game berdasarkan slug, contoh:
    - "mobile-legends-bang-bang"
    - "free-fire"
    - "steam-voucher-indonesia"
    """
    url = f"{BASE}/product/{slug}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        return _json_or_raw(r) or {}
    except Exception:
        return {}
        
# ====== MENU HELPERS ======
def show_short_menu(items, filter_fn=None):
    if filter_fn:
        items = filter_fn(items)

    if not items:
        return None

    print("\n💠 Pilih Item :\n")
    for idx, it in enumerate(items, 1):
        print(f"   {idx}. 💎 {it.get('name', '-'):<24} - Rp{_price_of(it)}")

    choice = input("\n💠 Pilih (1/2/...) / ENTER=Skip : ").strip()
    if choice == "":
        return None  # langsung skip, tidak tampilkan full list
    if choice.isdigit() and 1 <= int(choice) <= len(items):
        return items[int(choice) - 1]
    print(Fore.RED + "📍 Input tidak valid. Silakan pilih item." + Style.RESET_ALL)
    return None

# ====== GAME PROFILES ======
GAMES = {
    "mlbb": {
        "label": "Mobile Legends: Bang Bang",
        "slug": "mobile-legends-bang-bang",  # untuk GET /product/<slug>
        "need_zone": True,    # butuh userId + zoneId
        "prepare": True,      # ada prepare
        "force_product_id": None,
    },
    "freefire": {
        "label": "Free Fire (Garena)",
        "slug": "free-fire",
        "need_zone": False,   # hanya userId
        "prepare": True,      # ada prepare
        "force_product_id": None,
    },
    "steam": {
        "label": "Steam Wallet Voucher (ID)",
        "slug": "steam-voucher-indonesia",
        "need_zone": False,   # tidak butuh ID
        "prepare": False,     # TIDAK ada prepare → langsung inquiry
        "force_product_id": 21,  # dari sniff kamu
    },
    "roblox": {
        "label": "Roblox (Voucher Code)",
        "slug": "roblox",
        "need_zone": False,   # tidak butuh ID
        "prepare": False,     # TIDAK ada prepare → langsung inquiry
        "force_product_id": 32,  # dari sniff kamu
    },
}

# ====== API CALLS ======

def prepare_slug(slug: str, user_id: str, zone_id: str = "") -> dict:
    url = f"{BASE}/order/prepare/{slug}"
    params = {"userId": user_id}
    if zone_id and zone_id != "-":
        params["zoneId"] = zone_id
    r = s.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json() if "application/json" in r.headers.get("Content-Type", "") else {"data": r.text}


def inquiry(payload: Dict[str, Any]):
    url = f"{BASE}/order/inquiry"
    r = s.post(url, json=payload, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"inquiry {r.status_code}: {r.text}")
    return _json_or_raw(r)

# inquiry khusus untuk batch (menu 4)
def inquiry_safe(payload: Dict[str, Any]):
    url = f"{BASE}/order/inquiry"
    try:
        start = time.time()
        r = batch_session.post(url, headers=HEADERS, json=payload, timeout=BATCH_TIMEOUT)
        debug_print(f"{blue}⏱️ [inquiry_safe] {time.time()-start:.2f}s{reset}")
    except requests.exceptions.ReadTimeout:
        debug_print(f"⚠️ Timeout {url.split('/')[-1]}, retry sekali ...")
        time.sleep(1)
        r = batch_session.post(url, headers=HEADERS, json=payload, timeout=BATCH_TIMEOUT)
    try:
        js = r.json()
    except Exception:
        js = {"error": r.text}
    js["statusCode"] = r.status_code
    return js

def payment(payload: dict) -> dict:
    url = f"{BASE}/order/payment"
    r = s.post(url, json=payload, timeout=30)

    if r.status_code >= 400:
        raise RuntimeError(f"payment {r.status_code}: {r.text}")

    invoice_id = None
    js = None
    # Coba JSON lebih dulu
    try:
        js = r.json()
    except Exception:
        js = None

    if isinstance(js, dict):
        # 1) langsung dari root
        invoice_id = js.get("invoiceId")
        # 2) atau dari "data" yang bisa string ATAU dict
        if not invoice_id:
            data = js.get("data")
            if isinstance(data, str):
                invoice_id = data
            elif isinstance(data, dict):
                invoice_id = data.get("invoiceId")

    # Fallback: header Location
    if not invoice_id:
        loc = r.headers.get("Location") or r.headers.get("location")
        if loc and "/games/payment/" in loc:
            invoice_id = loc.rsplit("/", 1)[-1]

    # Fallback: regex dari body HTML/text
    if not invoice_id:
        m = re.search(r"/games/payment/([A-Z0-9]+)", r.text)
        if m:
            invoice_id = m.group(1)

    return {
        "invoiceId": invoice_id,
        "json": js,
        "text": r.text,
        "headers": dict(r.headers),
        "status": r.status_code,
    }

def payment_voucher(payload: dict) -> dict:
    url = f"{BASE}/order/payment"
    try:
        start = time.time()
        r = batch_session.post(url, headers=HEADERS, json=payload, timeout=BATCH_TIMEOUT)
        debug_print(f"{green}⏱️ [payment_voucher] {time.time()-start:.2f}s{reset}")
    except requests.exceptions.ReadTimeout:
        debug_print(f"⚠️ Timeout {url.split('/')[-1]}, retry sekali ...")
        time.sleep(1)
        r = batch_session.post(url, headers=HEADERS, json=payload, timeout=BATCH_TIMEOUT)

    if r.status_code >= 400:
        raise RuntimeError(f"payment {r.status_code}: {r.text}")

    invoice_id = None
    js = None
    # Coba JSON lebih dulu
    try:
        js = r.json()
    except Exception:
        js = None

    if isinstance(js, dict):
        # 1) langsung dari root
        invoice_id = js.get("invoiceId")
        # 2) atau dari "data" yang bisa string ATAU dict
        if not invoice_id:
            data = js.get("data")
            if isinstance(data, str):
                invoice_id = data
            elif isinstance(data, dict):
                invoice_id = data.get("invoiceId")

    # Fallback: header Location
    if not invoice_id:
        loc = r.headers.get("Location") or r.headers.get("location")
        if loc and "/games/payment/" in loc:
            invoice_id = loc.rsplit("/", 1)[-1]

    # Fallback: regex dari body HTML/text
    if not invoice_id:
        m = re.search(r"/games/payment/([A-Z0-9]+)", r.text)
        if m:
            invoice_id = m.group(1)

    return {
        "invoiceId": invoice_id,
        "json": js,
        "text": r.text,
        "headers": dict(r.headers),
        "status": r.status_code,
    }

def get_transaction(invoice_id: str):
    url = f"{BASE}/transaction/{invoice_id}"
    r = s.get(url, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"transaction {r.status_code}: {r.text}")
    return _json_or_raw(r)
    
def fetch_items_for(game_key: str):
    """Ambil definisi product + daftar item dari slug game."""
    prof = GAMES[game_key]
    prod = get_product(prof["slug"])  # kamu sudah punya get_product()
    items = (prod.get("items") or [])
    # titipkan productId ke tiap item (kalau ada)
    pid = prod.get("id") or prof.get("force_product_id") or 0
    for it in items:
        it["_productId"] = pid
    return prod, items

def build_inquiry_payload(game_key: str, picked: dict, user_id: str = "", zone_id: str = "", qty: int = 1):
    prof = GAMES[game_key]
    prod_id = int(picked.get("_productId") or picked.get("productId") or prof.get("force_product_id") or 0)
    data = {}
    if game_key == "mlbb":
        data = {"userId": str(user_id), "zoneId": str(zone_id)}
    elif game_key == "freefire":
        data = {"userId": str(user_id)}
    # steam: data tetap {}

    return {
        "productId": prod_id,
        "productItemId": int(picked["id"]),
        "data": data,
        "paymentChannelId": 73,
        "phoneNumber": PHONE_NUMBER if "PHONE_NUMBER" in globals() else "628783219212",
        "paymentPhoneNumber": "",
        "quantity": max(1, int(qty or 1)),
    }
    
def build_inquiry_payload_voucher(game_key: str, picked: dict, user_id: str = "", zone_id: str = "", qty: int = 1, voucher_code: str = ""):
    """Payload inquiry khusus jika ada voucher"""
    prof = GAMES[game_key]
    prod_id = int(picked.get("_productId") or picked.get("productId") or prof.get("force_product_id") or 0)
    data = {}
    if game_key == "mlbb":
        data = {"userId": str(user_id), "zoneId": str(zone_id)}
    elif game_key == "freefire":
        data = {"userId": str(user_id)}

    return {
        "productId": prod_id,
        "productItemId": int(picked["id"]),
        "data": data,
        "paymentChannelId": 73,
        "phoneNumber": PHONE_NUMBER if "PHONE_NUMBER" in globals() else "628783219212",
        "voucher": voucher_code,   # <--- beda dengan normal
        "referralCode": "",
        "paymentPhoneNumber": "",
        "quantity": max(1, int(qty or 1))
    }
    
    
def batch_check_voucher(uid, zid, kode, picked, game_key):
    try:
        # === STEP 1: Inquiry sekali untuk lock order_id ===
        INQUIRY_PAYLOAD = build_inquiry_payload_voucher(
            game_key, picked, uid, zid, voucher_code=kode
        )
        debug_print(f"[{ts()}] Inquiry Payload {uid}: {json.dumps(INQUIRY_PAYLOAD, indent=2)}")
        resp_inq = inquiry_safe(INQUIRY_PAYLOAD)
        debug_print(f"[{ts()}] Inquiry Resp {uid}: {resp_inq}")

        msg_inq = (resp_inq.get("message") or resp_inq.get("error") or "").lower()
        
        if "this voucher is not available at this time" in msg_inq:
            return f"⏳ {uid} Kode voucher belum berlaku"

        if str(resp_inq.get("statusCode")) == "404" and "invalid user account" in msg_inq:
            return f"❌ {uid} ID Game INVALID"

        if str(resp_inq.get("statusCode")) == "400":
            if "unavailable" in msg_inq:
                return f"🚫 {uid} Kuota voucher HABIS"
            elif "redeem limit" in msg_inq:
                return f"❌ {uid} ID Game LIMIT"
            else:
                return f"[{uid}] ⚠️ Error Inquiry: {msg_inq}"
                
        if str(resp_inq.get("statusCode")) in ("200", "201"):
            return f"✅ {uid} Voucher VALID"
    
    except Exception as e:
        print(f"[{idx}] ⚠️ {user_id} Error: {e}")
        
        
def menu_batch_checkout():
    while True:
        print("\n🚀 Batch Checkout Menu")
        print("   1. Checker Voucher")
        print("   2. Checkout Multi ID")
        print("   3. Cek Transaksi")
        print("   0. Kembali")
        pilih = input("\nPilih: ").strip()

        if pilih == "0":
            return

        elif pilih == "1":
            ids_file = input("📂 Path file IDs (misal ids.txt): ").strip()
            voc_input = input("📂 Voucher (kode langsung atau file .txt): ").strip()
            gsel = input("🎮 Game? (1=MLBB, 2=FreeFire): ").strip()
            game_key = ("mlbb","freefire")[int(gsel)-1]
        
            jam_str = input("⏰ Jam target (HH:MM:SS, default 15:00:00): ").strip()
            if jam_str:
                h, m, s = parse_target_time(jam_str)
            else:
                h, m, s = 15, 0, 0
            
            wait_until(h, m, s)
        
            # --- ambil daftar ID dari file ---
            with open(ids_file, encoding="utf-8") as f:
                ids = [ln.strip() for ln in f if ln.strip()]
        
            prod, items = fetch_items_for(game_key)
            picked = items[0]   # default ambil item pertama, atau bikin pilihan manual
        
            results = []
            for line in ids:
                parts = line.split()
                uid, zid = parts[0], (parts[1] if len(parts) > 1 else "-")
                kode = voc_input
                res = batch_check_voucher(uid, zid, kode, picked, game_key)
                results.append(res)
        
            print("\n📊 Hasil Checker Voucher:")
            for r in results:
                print(r)
            input("\nENTER untuk kembali")
            continue
            
        elif pilih == "2":
            ids_file = input("📂 Path file IDs (misal ids.txt): ").strip()
            voc_input = input("📂 Voucher (kode langsung atau file .txt): ").strip()
            gsel = input("🎮 Game? (1=MLBB, 2=FreeFire): ").strip()
            game_key = ("mlbb","freefire")[int(gsel)-1]
        
            jam_str = input("⏰ Jam target (HH:MM:SS, default 15:00:00): ").strip()
            if jam_str:
                h, m, s = parse_target_time(jam_str)
            else:
                h, m, s = 15, 0, 0
        
            if voc_input.endswith(".txt"):
                batch_checkout_fast(game_key, ids_file, voc_file=voc_input,
                                    start_hour=h, start_minute=m, start_second=s)
            else:
                batch_checkout_fast(game_key, ids_file, voc_file=None,
                                    start_hour=h, start_minute=m, start_second=s,
                                    kode_manual=voc_input)
            continue

        elif pilih == "3":
            run_menu3_batch_details()  # kamu sudah punya di script

        else:
            print("📍 Input tidak valid.")
# ====== PRODUCT LISTING & NORMALIZE ======

def _normalize_product_json(js: Any) -> Dict[str, Any]:
    """Samakan bentuk ke {id, name, items:[{id, productId, name, price, priceDiscountMobile, group}]}"""
    if isinstance(js, list):
        # Banyak endpoint mengembalikan list products → gabung jadi satu
        products = []
        for p in js:
            if isinstance(p, dict):
                products.append(p)
        return {"id": None, "name": "list", "items": _collect_items(products)}
    elif isinstance(js, dict):
        items = []
        if "items" in js and isinstance(js["items"], list):
            items = js["items"]
            pid = js.get("id") or js.get("productId")
            name = js.get("name") or js.get("title") or "product"
            return {"id": pid, "name": name, "items": _collect_items([js])}
        # Kadang bentuknya {data:{items:[...]}}
        data = js.get("data") if isinstance(js.get("data"), dict) else None
        if data and isinstance(data.get("items"), list):
            return {"id": data.get("id"), "name": data.get("name"), "items": _collect_items([data])}
    return {"id": None, "name": "unknown", "items": []}


def _collect_items(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in products:
        pid = p.get("id") or p.get("productId")
        name = p.get("name") or p.get("title")
        items = p.get("items") or p.get("variants") or []
        for it in items:
            row = {
                "id": it.get("id"),  # productItemId
                "productId": it.get("productId") or pid,
                "name": it.get("name"),
                "price": it.get("price"),
                "priceDiscount": it.get("priceDiscount"),
                "priceDiscountMobile": it.get("priceDiscountMobile"),
                "group": it.get("group"),
                "_productId": (it.get("productId") or pid),  # untuk inquiry
                "_price": _price_of(it),
            }
            out.append(row)
    return out


def list_products_mlbb(user_id: Optional[str] = None, zone_id: Optional[str] = None) -> Tuple[Optional[int], List[Dict[str, Any]]]:
    urls = [
        f"{BASE}/product/{PRODUCT_SLUG}",
        f"{BASE}/product?slug={PRODUCT_SLUG}",
        f"{BASE}/product/{PRODUCT_SLUG}?client=mobile",
    ]
    for u in urls:
        js = _json_or_raw(s.get(u, timeout=30))
        jsn = _normalize_product_json(js)
        items = jsn.get("items") or []
        if items:
            return jsn.get("id"), items
    # Fallback kecil lewat prepare (kadang mengisi cache/harga mobile)
    if user_id and zone_id:
        _ = prepare_slug(PRODUCT_SLUG, user_id, zone_id)
        js = _json_or_raw(s.get(f"{BASE}/product/{PRODUCT_SLUG}", timeout=30))
        jsn = _normalize_product_json(js)
        return jsn.get("id"), (jsn.get("items") or [])
    return None, []

# ====== MAIN ======

def main():
    while True:
        print(f"\n{BOLD}🧬 ⚔️ MENU ⚔️ 🧬{RESET}")
        print("\n   1. 🔁 Order Automatis")
        print("   2. 📊 Ringkasan order (harian)")
        print("   3. 📑 Detail order (cek & simpan)")
        print("   4. 🚀 Batch Checkout Cepat (file id+voc)") 
        mode = input("\n💠 Pilih / Back [b] : ").strip().lower()
        if mode == "b":
            return
        if mode not in ("1","2","3","4"):
            print(Fore.RED + "📍 Input tidak valid. " + Style.RESET_ALL)
            continue
        # route
        if mode == "1":
            pass
        elif mode == "2":
            run_menu2_summary()
            continue   # balik ke menu
        elif mode == "3":
            run_menu3_details()
            continue   # balik ke menu
        elif mode == "4":
            # yang lama dihapus/dikomentari
            menu_batch_checkout()
            continue
                  
        # === pilih game dulu ===
        print("\n🎮 Pilih Game :\n")
        print("   1) 👑 Mobile Legends: Bang Bang")
        print("   2) 🔫 Free Fire (Garena)")
        print("   3) 👾 Steam Wallet Voucher (ID)")
        print("   4) 🤖 Roblox (Voucher Code)")
        while True:
            gsel = input("\n💠 Pilih (1/2/3) : ").strip()
            if gsel in ("1", "2", "3", "4"):
                break
            print("📍 Input tidak valid. Silakan pilih 1/2/3.")
        
        game_key = ("mlbb", "freefire", "steam", "roblox")[int(gsel)-1]
        prof = GAMES[game_key]
        
        # === input ID sesuai kebutuhan game ===
        user_id, zone_id = "", ""
        if game_key == "mlbb":
            raw_ids = input("️👉 Input Game ID (userId zoneId, Multi pisah Koma) : ").strip()
            pairs = _parse_user_zone_list(raw_ids)     # fungsi kamu yg lama
            if not pairs:
                print("📍 Tidak ada game ID yang valid.")
                continue
        elif game_key == "freefire":
            raw_ids = input("🎃 Input Game ID (userId saja, multi pisah koma): ").strip()
            ids = [x.strip() for x in raw_ids.split(",") if x.strip().isdigit()]
            if not ids:
                print("📍 Tidak ada game ID yang valid.")
                continue
            pairs = [(uid, "-") for uid in ids]
        else:
            # steam: tidak perlu ID, tapi kita samakan format pairs agar loop di bawah tetap reuse
            pairs = [("VOUCHER","-")]
                
        # ===== Konfigurasi repeat =====
        raw_rep = input("🎯 Target per ID? (default 1; Multi '1,2,1'): ").strip()
        repeats = []
        if raw_rep:
            try:
                repeats = [max(1, int(x.strip() or "1")) for x in raw_rep.split(",")]
            except Exception:
                repeats = []
        if not repeats:
            repeats = [1] * len(pairs)
        elif len(repeats) < len(pairs):
            repeats += [repeats[-1]] * (len(pairs) - len(repeats))
        else:
            repeats = repeats[:len(pairs)]
        
        delay_s = 0.5  # jeda default antar invoice saat repeat > 1
        
        # ===== Eksekusi per-ID =====
        ASK_ITEM_EVERY_ID = False
        picked_cache = None
        if GAMES.get(game_key, {}).get("prepare") and pairs:
            uid0, zid0 = pairs[0]
            try:
                _ = prepare_slug(GAMES[game_key]["slug"], uid0, zid0)
            except Exception as e:
                print(f"❌ Prepare awal gagal: {e}")
        
        # Ambil daftar item untuk ditampilkan di menu awal
        prod, items = fetch_items_for(game_key)
        if not items:
            print("🧨 Tidak ada item di katalog.")
            return
        items.sort(key=_price_of)
        # --- pilih item sekali di awal ---
        picked = show_short_menu(items, GAME_SHORT_MENU.get(game_key))
        if picked is None:
            print("📢 Skip item...")
            continue
            while True:
                c = input("\n💠 Pilih (1/2/3/...) : ").strip()
                if c.isdigit() and 1 <= int(c) <= len(items):
                    picked = items[int(c)-1]
                    break
                print("📍 Input tidak valid. Silakan pilih item.")
        
        # simpan pilihan agar dipakai semua target
        if picked is not None:
            picked_cache = picked
        for idx, (user_id, zone_id) in enumerate(pairs, 1):
            if not ASK_ITEM_EVERY_ID and picked_cache:
                picked = picked_cache
                try:
                    _ = prepare_slug(GAMES[game_key]["slug"], user_id, zone_id)
                except Exception as e:
                    print(f"❌ Prepare gagal untuk {user_id} {zone_id}: {e}")
                    continue
                    
            print("\n=====================================")
            print(f"🎯 Target {idx}/{len(pairs)} : {user_id} {zone_id}")
            print(f"🍀 Item  : {picked.get('name')}")
            print(f"🪙 Harga : Rp{_price_of(picked)}")
    
            # Repeat pembuatan invoice untuk ID ini
            n_repeat = repeats[idx - 1]
            for r in range(1, n_repeat + 1):
                print(f"\n⏳ Proses {r}/{n_repeat} ...")

                # ===== STEP 2: INQUIRY =====
                try:
                    # bikin payload inquiry
                    INQUIRY_PAYLOAD = build_inquiry_payload(game_key, picked, user_id, zone_id, qty=1)
                
                    # kalau game ini butuh prepare (MLBB / Free Fire), jalankan dulu
                    if GAMES.get(game_key, {}).get("prepare"):
                        try:
                            _ = prepare_slug(GAMES[game_key]["slug"], user_id, zone_id)
                        except Exception as e:
                            print(f"❌ Prepare gagal untuk {user_id} {zone_id}: {e}")
                            continue
                
                    # inquiry selalu dijalankan untuk buat orderId
                    resp = inquiry(INQUIRY_PAYLOAD)
                
                    # setelah extract_order_id(resp)
                    order_id = extract_order_id(resp)
                    if not order_id:
                        msg = None
                        if isinstance(resp, dict):
                            msg = (
                                resp.get("message")
                                or resp.get("error")
                                or (resp.get("data") or {}).get("message")
                            )
                        print(f"❌ UserID / Game ID salah. {f'Detail: {msg}' if msg else ''}")
                        input("\nENTER untuk kembali")
                        return
                
                except Exception as e:
                    print(f"❌ Inquiry gagal: {e}")
                    input("\nENTER untuk kembali")
                    return
                
                # ===== STEP 3: PAYMENT (disembunyikan, error saja) =====
                try:
                    pay = payment({
                        "orderId": order_id,
                        "paymentChannelId": 73,
                        "phoneNumber": "628783219212",  # ganti jika sudah ada variabel no HP
                        "paymentPhoneNumber": "",
                        "quantity": 1,
                        "invoiceUrl": "https://gopay.co.id/games/payment/",
                    })
                
                    # ambil invoice_id
                    invoice_id = None
                    if isinstance(pay, dict):
                        invoice_id = pay.get("invoiceId") or (pay.get("data") or {}).get("invoiceId")
                
                    if not invoice_id:
                        raise RuntimeError("invoiceId tidak terdeteksi")
                
                except Exception as e:
                    print(f"❌ Payment gagal: {e}")
                    continue
                # STEP 4: TRANSACTION (ambil status & link) — tampilkan ringkas
                status, total, act = "", 0, {}
                try:
                    trx = get_transaction(invoice_id)
                    if isinstance(trx, dict):
                        status = trx.get("status")
                        total  = trx.get("totalAmount") or trx.get("amount") or 0
                        act    = trx.get("actionPayment") or {}
                except Exception as e:
                    print(f"[WARN] get_transaction error: {e}")
    
                pay_link = (act or {}).get("paymentDirect") or (act or {}).get("deeplinkRedirect") or ""
                inv_url  = f"https://gopay.co.id/games/payment/{invoice_id}"
                print(f"✅ Link Payment: {pay_link}" if pay_link else "✅ Link Payment: (tidak tersedia)")
                print(f"✅ Link Invoice: {inv_url}")
    
                # --- simpan ke file ---
                log_csv, log_txt = _log_paths_for(game_key)  # <— tambahkan baris ini
                
                _append_csv({
                    "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "userId": str(user_id),
                    "zoneId": str(zone_id),
                    "productId": str(INQUIRY_PAYLOAD.get("productId") or picked.get("_productId") or ""),
                    "productItemId": str(picked.get("id") or ""),
                    "itemName": picked.get("name") or "",
                    "price": _price_of(picked),
                    "orderId": order_id,
                    "invoiceId": invoice_id,
                    "status": status,
                    "amount": total,
                    "deeplink": (act or {}).get("deeplinkRedirect") or "",
                    "invoiceUrl": inv_url,
                }, path=log_csv)
                
                _append_paylink(str(user_id), str(zone_id), picked.get("name") or "",
                                invoice_id, pay_link, path=log_txt)
    
                # jeda antar invoice kalau repeat > 1
                if r < n_repeat:
                    time.sleep(delay_s)
        print()
        print(f"   ↳ CSV  : {log_csv}")
        print(f"   ↳ TXT  : {log_txt}")
        print("\n🎯 Semua target selesai diproses.")
        input("\n⤵️  ENTER untuk kembali")
    return

if __name__ == "__main__":
    BOLD = "\033[1m"
    RESET = "\033[0m"
    print(f"{BOLD}===================================={RESET}")
    print(f"{BOLD}            GOPAYGAMES             {RESET}")
    print(f"{BOLD}   Auto Checkout (Mobile Legend)   {RESET}")
    print(f"{BOLD}===================================={RESET}")
    try:
        main()
    except KeyboardInterrupt:
        print("\nDibatalkan.")
