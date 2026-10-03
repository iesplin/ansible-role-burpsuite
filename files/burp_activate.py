#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pexpect",
# ]
# ///
"""Automated Burp Suite activation, with additional download of the CA public certificate"""

import argparse
import filecmp
import os
import pexpect
import shutil
import signal
import sys
import tempfile
import time
import urllib.error
import urllib.request

from pathlib import Path
from xml.etree.ElementTree import parse

ACTIVATION_TIMEOUT = 300
ACTIVATION_POLL_INTERVAL = 10
# Seconds to wait for any single prompt from Burp Suite
EXPECT_TIMEOUT = 120
# Burp's proxy listener
CACERT_URL = "http://localhost:8080/cert"
CACERT_RETRIES = 18
CACERT_RETRY_INTERVAL = 10

# prefs.xml entry keys
PREFS_KEYS = {
    "eula": "burp.eula",
    "license": "license1",
    "cacert": "caCert",
}


def check_prefs_entries(prefs_file: Path) -> dict[str, bool]:
    """Return which of the PREFS_KEYS entries exist in prefs.xml"""
    keys = set()
    if prefs_file.is_file():
        keys = {entry.get("key") for entry in parse(prefs_file).iter("entry")}
    return {name: key in keys for name, key in PREFS_KEYS.items()}


def is_activated(prefs_entries: dict[str, bool], is_pro: bool) -> bool:
    """Return whether the eula, and for Pro the license, have been accepted"""
    if is_pro:
        return prefs_entries["eula"] and prefs_entries["license"]
    return prefs_entries["eula"]


def wait_for_activation(prefs_file: Path, is_pro: bool) -> bool:
    """Poll prefs.xml until Burp Suite has finished activation process"""
    deadline = time.monotonic() + ACTIVATION_TIMEOUT
    while True:
        prefs_entries = check_prefs_entries(prefs_file)
        if is_activated(prefs_entries, is_pro) and prefs_entries["cacert"]:
            return True
        if time.monotonic() >= deadline:
            print(f"[!] Burp Suite did not finish activating within {ACTIVATION_TIMEOUT}s")
            return False
        time.sleep(ACTIVATION_POLL_INTERVAL)


def activate_burp(pexpect_child: pexpect.spawn, license_key: str | None) -> bool:
    """Send responses for Burp Suite activation"""
    # Prompt order for the installer:
    #   license agreement -> license key -> (pro only) activation method -> activated
    expect_options = [
        "Do you accept the license agreement",
        "press Enter to use the Community Edition",
        "Enter preferred activation method",
        "Your license is successfully installed and activated.",
        "The supplied license key was not recognized"
    ]
    while True:
        try:
            i = pexpect_child.expect(expect_options, timeout=EXPECT_TIMEOUT)
        except pexpect.TIMEOUT:
            print(f"[!] Timed out after {EXPECT_TIMEOUT}s waiting for a Burp Suite activation prompt")
            return False
        except pexpect.EOF:
            print("[!] Burp Suite exited before activation completed")
            return False
        if i == 0:
            pexpect_child.sendline("y")
        elif i == 1:
            if not license_key:
                # Enter selects the Community Edition
                pexpect_child.sendline("")
                break
            pexpect_child.sendline(license_key.strip())
        elif i == 2:
            pexpect_child.sendline("o")
        elif i == 3:
            break
        elif i == 4:
            print("[!] Burp Suite did not recognize the supplied license key")
            return False
    return True


def download_cacert(cacert_path: Path) -> bool:
    """Attempt to download public cacert"""
    with tempfile.TemporaryDirectory() as temp_cacert_dir:
        temp_cacert_path = Path(temp_cacert_dir) / "cacert.der"
        for _ in range(CACERT_RETRIES):
            try:
                urllib.request.urlretrieve(CACERT_URL, temp_cacert_path)
                if not cacert_path.is_file() or not filecmp.cmp(temp_cacert_path, cacert_path, shallow=False):
                    shutil.move(temp_cacert_path, cacert_path)
                    cacert_path.chmod(0o644)
                    print("[+] Certificate downloaded/updated")
                return True
            except urllib.error.URLError:
                time.sleep(CACERT_RETRY_INTERVAL)
            except Exception as e:
                print(f"[!] Unexpected error downloading CA cert: {e}")
                return False
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Automated Burp Suite activation, with additional download of the CA public certificate.",
        epilog="Set BURP_LICENSE_KEY to activate the Professional edition; "
               "without it the Community edition is used."
    )
    parser.add_argument("burpdir", help="Burp Suite directory")
    parser.add_argument("--cacert-path", help="Download path for the Burp Suite CA public certificate.")
    args = parser.parse_args()

    exit_status = 0

    license_key = os.getenv("BURP_LICENSE_KEY")

    cacert_path = Path(args.cacert_path) if args.cacert_path else None

    burp_dir = Path(args.burpdir)
    if not burp_dir.is_dir():
        print(f"[!] Directory {burp_dir} does not exist")
        sys.exit(1)

    java_path = burp_dir / "jre/bin/java"
    if not java_path.is_file():
        print(f"[!] Java executable not found at {java_path}")
        sys.exit(1)

    burp_jar_path = burp_dir / "burpsuite.jar"
    if not burp_jar_path.is_file():
        print(f"[!] Could not find burpsuite.jar in {burp_dir}")
        sys.exit(1)

    child = None
    try:
        is_pro = bool(license_key)

        # Start Burp Suite in headless mode
        burp_args = ["-Djava.awt.headless=true", "-jar", str(burp_jar_path)]
        child = pexpect.spawn(str(java_path), burp_args, encoding="UTF-8")
        # Log only what Burp writes, with pty echo off, so the license key is never written to stdout
        child.setecho(False)
        child.logfile_read = sys.stdout

        # Check prefs.xml file to see if Burp Suite is already activated
        burp_prefs_file = Path.home() / ".java/.userPrefs/burp/prefs.xml"
        prefs_entries = check_prefs_entries(burp_prefs_file)
        if is_activated(prefs_entries, is_pro):
            print("[+] Burp Suite already activated")
        else:
            # Respond to Burp Suite prompts to activate
            if not activate_burp(child, license_key):
                sys.exit(1)

            if not wait_for_activation(burp_prefs_file, is_pro):
                sys.exit(1)

        # If cacert argument provided
        if cacert_path:
            if not cacert_path.parent.is_dir():
                print("[!] Directory for CA cert does not exist")
                sys.exit(1)

            # Check that Burp Suite is already activated and the cacert is generated
            prefs_entries = check_prefs_entries(burp_prefs_file)
            if is_activated(prefs_entries, is_pro) and prefs_entries["cacert"]:
                downloaded = download_cacert(cacert_path)
                if not downloaded:
                    print("[!] Could not download CA cert")
                    exit_status = 1
            else:
                print("[!] Burp Suite must complete activation prior to downloading CA cert")
                exit_status = 1

    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        exit_status = 1
    finally:
        # Terminate Burp Suite process
        if child is not None:
            if child.isalive():
                child.kill(signal.SIGTERM)
            child.close()

    sys.exit(exit_status)

