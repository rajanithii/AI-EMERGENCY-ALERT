#!/usr/bin/env python
"""
Generate Self-Signed Certificate for HTTPS
This enables geolocation API access from non-localhost IPs
"""
import os
import sys
from pathlib import Path

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    import datetime
except ImportError:
    print("❌ Missing cryptography library. Installing...")
    os.system("pip install cryptography -q")
    print("✅ Installed. Run this script again.")
    sys.exit(0)

def generate_self_signed_cert(cert_file: str, key_file: str, hostname: str = "182.18.2.8"):
    """Generate a self-signed certificate"""
    
    if Path(cert_file).exists() and Path(key_file).exists():
        print(f"✅ Certificate already exists at {cert_file}")
        return
    
    print(f"🔐 Generating self-signed certificate for {hostname}...")
    
    # Create directory
    Path(cert_file).parent.mkdir(exist_ok=True)
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Generate certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Tamil Nadu"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Trichy"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"LifeLine"),
        x509.NameAttribute(NameOID.COMMON_NAME, hostname),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(hostname),
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256(), default_backend())
    
    # Write certificate
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    print(f"✅ Certificate saved to {cert_file}")
    
    # Write private key
    with open(key_file, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    print(f"✅ Private key saved to {key_file}")

if __name__ == "__main__":
    cert_file = "certs/cert.pem"
    key_file = "certs/key.pem"
    generate_self_signed_cert(cert_file, key_file)
    print("\n✨ Certificate ready! Now run: python start_https_server.py")
