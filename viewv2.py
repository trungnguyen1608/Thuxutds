#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
viewv2.py — Tool view TikTok + rút gọn Link4m + chế độ bảo trì / admin key
"""

import os
import json
import time
import random
import requests
import re
import threading
import secrets
from hashlib import md5
from time import time as T
from urllib.parse import quote_plus

# URL tới file keys.json trên GitHub Pages của bạn
GITHUB_KEYS_URL = "https://trungnguyen1608.github.io/link4m-key-dashboard/keys.json"

# --- Hàm lấy keys từ GitHub ---
def fetch_keys_from_github():
    try:
        r = requests.get(GITHUB_KEYS_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[!] Không tải được keys.json từ GitHub: {e}")
        return {}

# --- Rút gọn link bằng Link4m ---
def shorten_with_link4m_using_token(long_url: str, token: str) -> dict:
    try:
        api = f"https://link4m.co/api-shorten/v2?api={token}&url={quote_plus(long_url)}"
        r = requests.get(api, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "success" and data.get("shortenedUrl"):
            return {"success": True, "short_url": data["shortenedUrl"]}
        else:
            return {"success": False, "error": data}
    except Exception as e:
        return {"success": False, "error": str(e)}

# --- Logic view TikTok ---
def random_device():
    devices = ["Pixel 6", "Pixel 5", "Samsung Galaxy S21", "Oppo Reno 8", "Xiaomi Mi 11"]
    os_versions = ["12", "13", "14"]
    return random.choice(devices), random.choice(os_versions), random.randint(26, 34)

class Signature:
    def __init__(self, params: str, data: str, cookies: str) -> None:
        self.params = params; self.data = data; self.cookies = cookies
    def hash(self, data: str) -> str:
        return str(md5(data.encode()).hexdigest())
    def calc_gorgon(self) -> str:
        g = self.hash(self.params)
        g += self.hash(self.data) if self.data else "0"*32
        g += self.hash(self.cookies) if self.cookies else "0"*32
        g += "0"*32
        return g
    def get_value(self):
        return self.encrypt(self.calc_gorgon())
    def encrypt(self, data: str):
        unix = int(T()); length = 0x14
        key = [0xDF,0x77,0xB9,0x40,0xB9,0x9B,0x84,0x83,0xD1,0xB9,0xCB,0xD1,0xF7,0xC2,0xB9,0x85,0xC3,0xD0,0xFB,0xC3]
        pl = []
        for i in range(0,12,4):
            t = data[8*i:8*(i+1)]
            for j in range(4):
                pl.append(int(t[j*2:(j+1)*2],16))
        pl.extend([0x0, 0x6, 0xB, 0x1C])
        H = int(hex(unix),16)
        pl += [(H&0xFF000000)>>24, (H&0x00FF0000)>>16, (H&0x0000FF00)>>8, (H&0x000000FF)>>0]
        e = [a ^ b for a, b in zip(pl, key)]
        for i in range(length):
            C = self.reverse(e[i])
            D = e[(i+1) % length]
            F = self.rbit(C ^ D)
            H = ((F ^ 0xFFFFFFFF) ^ length) & 0xFF
            e[i] = H
        r = "".join(self.hex_string(x) for x in e)
        return {"X-Gorgon": "840280416000" + r, "X-Khronos": str(unix)}

    def rbit(self, n):
        s = bin(n)[2:].zfill(8)
        return int(s[::-1],2)
    def hex_string(self, n):
        s = hex(n)[2:]
        return s if len(s) == 2 else "0" + s
    def reverse(self, n):
        s = self.hex_string(n)
        return int(s[1:] + s[:1], 16)

ua_list = [
    "com.ss.android.ugc.trill/400304 (Linux; Android 13; Pixel 6)",
    "com.ss.android.ugc.trill/400304 (Linux; Android 12; Samsung Galaxy S21)",
    "com.ss.android.ugc.trill/400304 (Linux; Android 14; Xiaomi Mi 11)"
]

def send_view_loop(video_id):
    while True:
        device_type, os_version, os_api = random_device()
        params = (f"channel=googleplay&aid=1233&app_name=musical_ly&version_code=400304"
                  f"&device_platform=android&device_type={device_type.replace(' ','+')}"
                  f"&os_version={os_version}&device_id={random.randint(600000000000000,699999999999999)}"
                  f"&os_api={os_api}&app_language=vi&tz_name=Asia%2FHo_Chi_Minh")
        url = f"https://api16-core-c-alisg.tiktokv.com/aweme/v1/aweme/stats/?{params}"
        cookies = {"sessionid": secrets.token_hex(8)}
        data = {"item_id": video_id, "play_delta": 1, "action_time": int(time.time())}
        sig = Signature(params=params, data=str(data), cookies=str(cookies)).get_value()
        headers = {
            "User-Agent": random.choice(ua_list),
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Gorgon": sig["X-Gorgon"], "X-Khronos": sig["X-Khronos"]
        }
        try:
            r = requests.post(url, data=data, headers=headers, cookies=cookies, timeout=10)
            if "application/json" in r.headers.get("Content-Type", ""):
                resp = r.json()
                print("✅ View |", resp.get("status_code"))
            else:
                print("⚠️ Response:", r.text[:80])
        except Exception as e:
            print("❌ Lỗi gửi view:", e)
            time.sleep(2)
        time.sleep(random.uniform(0.3, 1.2))

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("=== Tool view + Link4m (Admin Trung bá vũ trụ) ===")

    data = fetch_keys_from_github()
    if data.get("maintenance"):
        print("\n🚧 TOOL ĐANG BẢO TRÌ 🚧")
        admin_input = input("Nếu bạn là admin, nhập admin key để tiếp tục: ").strip()
        if admin_input == data.get("admin_key"):
            print("✅ Xác thực thành công — chào Admin Trung bá vũ trụ!")
        else:
            print("❌ Hệ thống đang bảo trì. Vui lòng quay lại sau.")
            return

    link = input("Nhập link TikTok hoặc link bất kỳ: ").strip()
    if not link:
        print("Không có link.")
        return

    key24 = data.get("key_24h", {}).get("token")
    token = key24 if key24 else (data.get("permanent", [])[0] if data.get("permanent") else None)
    if not token:
        print("❌ Không có token hợp lệ.")
        return

    print("Đang rút gọn link …")
    res = shorten_with_link4m_using_token(link, token)
    if res.get("success"):
        print("🔗 Link rút gọn:", res["short_url"])
    else:
        print("❌ Lỗi:", res.get("error"))
        # fallback: dùng link gốc
    do_view = input("Chạy auto-view? (y/N): ").strip().lower()
    if do_view != "y":
        print("Kết thúc.")
        return

    # Lấy video_id từ link gốc
    headers_id = {'User-Agent': 'Mozilla/5.0'}
    try:
        html = requests.get(link, headers=headers_id, timeout=10).text
        m = re.search(r'"video":\{"id":"(\d+)"', html)
        if not m:
            print("❌ Không tìm thấy ID video.")
            return
        video_id = m.group(1)
    except Exception as e:
        print("❌ Lỗi khi lấy ID:", e)
        return

    print("Bắt đầu gửi view …")
    threads = []
    for i in range(100):
        t = threading.Thread(target=send_view_loop, args=(video_id,))
        t.daemon = True
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()