#!/usr/bin/env python
"""
StartHTTPS Server with Self-Signed Certificate
This allows geolocation API to work from non-localhost IPs
"""
import uvicorn
import os
import ssl
from pathlib import Path

# Generate self-signed certificate if it doesn't exist
cert_dir = Path("./certs")
cert_file = cert_dir / "cert.pem"
key_file = cert_dir / "key.pem"

if not cert_file.exists() or not key_file.exists():
    print("🔐 Generating self-signed certificate...")
    cert_dir.mkdir(exist_ok=True)
    
    # Generate certificate using openssl
    os.system(f'openssl req -x509 -newkey rsa:4096 -nodes -out "{cert_file}" -keyout "{key_file}" -days 365 -subj "/CN=182.18.2.8"')
    print(f"✅ Certificate created at {cert_file} and {key_file}")
else:
    print(f"✅ Using existing certificate at {cert_file}")

# Run HTTPS server
print("🚀 Starting HTTPS server on https://182.18.2.8:8000")
print("⚠️  Browser will show security warning - click 'Advanced' then 'Proceed'")
print()

uvicorn.run(
    "newalert.backend.main:app",
    host="182.18.2.8",
    port=8000,
    reload=True,
    ssl_certfile=str(cert_file),
    ssl_keyfile=str(key_file),
)
