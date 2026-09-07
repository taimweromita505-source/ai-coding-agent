#!/usr/bin/env python3
"""
Network access helper - shows local IP and QR code for easy mobile access
"""

import socket
import subprocess
import sys
from pathlib import Path

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def generate_qr_code(url):
    """Generate QR code using Python"""
    try:
        # Try to use qrcode library
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        qr.print_ascii(invert=True)
    except ImportError:
        # Fallback: provide URL
        print(f"\nScan this URL: {url}")
        print("Install a QR code scanner app and scan the text above")

def main():
    port = 8080
    ip = get_local_ip()
    url = f"http://{ip}:{port}"
    
    print("=" * 60)
    print("  AI CODING AGENT - NETWORK ACCESS")
    print("=" * 60)
    print()
    print(f"Local access:    http://localhost:{port}")
    print(f"Network access:  {url}")
    print()
    print("To access from mobile devices:")
    print(f"1. Ensure phone and computer are on same WiFi")
    print(f"2. Open browser on phone and go to: {url}")
    print(f"3. Add to home screen for app-like experience")
    print()
    print("QR Code:")
    generate_qr_code(url)
    print()
    print("=" * 60)
    print("Press Enter to exit...")
    input()

if __name__ == "__main__":
    main()
