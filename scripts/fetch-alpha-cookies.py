#!/usr/bin/env python3
"""Use Chrome cookies to fetch alpha details via API."""

import json
import os
import sys
import time
from pathlib import Path
from http.cookiejar import MozillaCookieJar

sys.path.insert(0, '/Users/zpdedn/Documents/project/Worldquantbrain/scripts')

API_BASE = "https://api.worldquantbrain.com"

ALPHA_IDS = [
    'akAJeKo2', 'QP2eOklr', 'QP2j0XlG', 'qMPbYbjE', 'RR2XQ89d',
    'wpn1GX71', 'vRe9G3bz', 'O0b58J1d', 'LLglqor2', '9qaomYb9'
]

def load_chrome_cookies():
    """Load cookies from Chrome's SQLite database."""
    import sqlite3
    import tempfile

    cookie_db = Path.home() / 'Library/Application Support/Google/Chrome/Profile 1/Cookies'
    if not cookie_db.exists():
        cookie_db = Path.home() / 'Library/Application Support/Google/Chrome/Default/Cookies'

    temp_db = tempfile.mktemp(suffix='.db')
    import shutil
    shutil.copy(cookie_db, temp_db)

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT host, name, value, path, is_secure, expires_utc FROM cookies WHERE host LIKE '%worldquantbrain%'")
    cookies = cursor.fetchall()
    conn.close()
    os.unlink(temp_db)

    return cookies

def main():
    print("Loading Chrome cookies...")
    cookies = load_chrome_cookies()
    print(f"Found {len(cookies)} BRAIN cookies")

    if not cookies:
        print("No cookies found!")
        return

    for cookie in cookies:
        print(f"  {cookie[0]}: {cookie[1]}={cookie[2][:30]}...")

    import requests

    session = requests.Session()
    for cookie in cookies:
        host, name, value, path, is_secure, expires = cookie
        session.cookies.set(name, value, domain=host, path=path)

    print("\nTesting API access...")

    # Try to fetch one alpha
    response = session.get(f"{API_BASE}/alphas/{ALPHA_IDS[0]}", timeout=30)
    print(f"Response status: {response.status_code}")
    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2)[:500])
    else:
        print(f"Error: {response.text[:200]}")

if __name__ == '__main__':
    main()