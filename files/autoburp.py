#!/usr/bin/env python3
"""Helper script to automate activation/licensing for Burp Suite"""

import argparse
import filecmp
import os
import pexpect.popen_spawn
import shutil
import signal
import sys
import tempfile
import time
import urllib.request
from defusedxml.ElementTree import parse


def check_burp_status(prefs_file, product_type):
    """Return status for existance of entries in prefs.xml"""
    burp_status = {
        "eula": False,
        "license": False,
        "cacert": False
    }
    if os.path.isfile(burp_prefs_file):
        root = parse(burp_prefs_file)
        for entry in root.iter("entry"):
            if entry.attrib["key"] == "eula{type}".format(type=product_type):
                burp_status["eula"] = True
            if entry.attrib["key"] == "license1":
                burp_status["license"] = True
            if entry.attrib["key"] == "caCert":
                burp_status["cacert"] = True
    return burp_status


def find_burp_jar(burp_dir):
    """Search and return the path for the Burp Suite jar file"""
    burp_jar_path = ""
    burp_jar_files = [ f for f in os.listdir(args.burpdir) if f.startswith("burpsuite_") and f.endswith(".jar")]
    if len(burp_jar_files) > 0:
        burp_jar_path = os.path.join(args.burpdir, burp_jar_files[0])
    return burp_jar_path


def activate_burp(pexpect_child, license_key):
    """Send responses for Burp Suite activation"""
    expect_options = [
        "Do you accept the terms and conditions\\? \\(y/n\\)",
        "Do you accept the license agreement\\? \\(y/n\\)",
        "please paste your license key below.",
        "Enter preferred activation method",
        "Your license is successfully installed and activated."
    ]
    while True:
        i = pexpect_child.expect(expect_options)
        if i == 0:
            pexpect_child.sendline("y")
            break
        elif i == 1:
            pexpect_child.sendline("y")
        elif i == 2:
            # Remove any extra spaces or new lines
            license_key = license_key.lstrip().rstrip()
            pexpect_child.sendline(license_key)
        elif i == 3:
            pexpect_child.sendline("o")
        elif i == 4:
            break
        else:
            return False
    return True


def download_cacert(cacert_path):
    """Attempt to download public cacert"""
    with tempfile.TemporaryDirectory() as temp_cacert_dir:
        temp_cacert_path = os.path.join(temp_cacert_dir, "cacert.der")
        # Attempt to download
        for retry in range(18):
            try:
                urllib.request.urlretrieve("http://localhost:8080/cert", temp_cacert_path)
                # If ca cert doesn't exist or doesn't match
                if not os.path.isfile(cacert_path) or not filecmp.cmp(temp_cacert_path, cacert_path):
                    shutil.move(temp_cacert_path, cacert_path)
                    os.chmod(cacert_path, 0o644)
                    print("[+] Certificate downloaded/updated")
                return True
            except urllib.error.URLError as e:
                time.sleep(10)
            except Exception as e:
                print(e)
                return False
    return False


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Burp Suite license/agreement.")
    parser.add_argument("burpdir", help="Burp Suite directory")
    parser.add_argument("--license-key", help="Burp Suite Pro license key")
    parser.add_argument("--cacert-path", help="Download path for the Burp Suite CA public certificate.")
    args = parser.parse_args()

    license_key = None
    cacert_path = None

    exit_status = 0
    burp_dir = args.burpdir
    cacert_path = args.cacert_path
    
    # Check BURP_LICENSE_KEY env var first
    if os.getenv('BURP_LICENSE_KEY'):
        license_key = os.getenv('BURP_LICENSE_KEY')
    elif args.license_key:
        license_key = args.license_key

    # Check Burp Suite directory exists
    if not os.path.isdir(burp_dir):
        print(f"[!] Directory {burp_dir} does not exist.")
        sys.exit(1)

    java_path = os.path.join(burp_dir, "jre/bin/java")

    # Check java executable
    if not os.path.isfile(java_path):
        print(f"[!] Java executable not found at {java_path}")
        sys.exit(1)

    # Locate Burp Suite jar
    burp_jar_path = find_burp_jar(burp_dir)

    if not burp_jar_path:
        print(f"Could not find jar file in {burp_dir}")
        sys.exit(1)
    else:
        try:
            # Determine product type from jar filename
            if "pro" in os.path.basename(burp_jar_path):
                product_type = "pro"
            else:
                product_type = "community"

            # Start Burp Suite in headless mode
            burp_command = f"{java_path} --illegal-access=permit -Djava.awt.headless=true -jar '{burp_jar_path}'"
            child = pexpect.popen_spawn.PopenSpawn(burp_command, encoding='UTF-8')
            child.logfile = sys.stdout

            # Check prefs.xml file to see if Burp Suite is already activated/licensed
            burp_prefs_file = os.path.join(os.path.expanduser("~"), ".java/.userPrefs/burp/prefs.xml")
            burp_status = check_burp_status(burp_prefs_file, product_type)
            if (burp_status["eula"] and
                    (product_type == "community" or (product_type == "pro" and burp_status["license"]))):
                print("Burp Suite already licensed/eula accepted")
            else:
                # If activating Pro version, check license key argument was provided
                if (not license_key
                    and product_type == "pro"):
                    print("[!] License key not provided")
                    sys.exit(1)

                # Respond to Burp Suite prompts to activate
                activated_status = activate_burp(child, license_key)
                if not activated_status:
                    print("[!] Error encountered when activating Burp Suite")
                    sys.exit(1)
                else:
                    # Wait for Burp Suite to complete activation processes
                    while True:
                        burp_status = check_burp_status(burp_prefs_file, product_type)
                        if (burp_status["eula"]
                            and (product_type == "community" or (product_type == "pro" and burp_status["license"]))
                            and burp_status["cacert"]):
                            break
                        time.sleep(10)

            # If cacert argument provided
            if cacert_path:
                # Check if directory exists
                if not os.path.isdir(os.path.dirname(cacert_path)):
                    print("[!] Directory for CA cert does not exist")
                    sys.exit(1)

                # Check that Burp Suite is already activated and the cacert is generated
                burp_status = check_burp_status(burp_prefs_file, product_type)
                if (burp_status["eula"]
                    and (product_type == "community" or (product_type == "pro" and burp_status["license"]))
                    and burp_status["cacert"]):
                    # Attempt to download ca public cert
                    downloaded = download_cacert(cacert_path)
                    if not downloaded:
                        print("[!] Could not acquire CA cert")
                        exit_status = 1
                else:
                    print("[!] Burp Suite must complete activation prior to downloading CA cert")
                    exit_status = 1

        except Exception as e: 
            print(e)
            exit_status = 1
        finally:
            # Terminate Burp Suite process
            child.kill(signal.SIGTERM)

    sys.exit(exit_status)
