#!/usr/bin/env python3
"""Helper script to automate activation/licensing for Burp Suite"""

import argparse
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
    """Return status for eula* and license1 entries in prefs.xml"""
    eula_accepted = False
    license_activated = False
    cacert_generated = False
    if os.path.exists(burp_prefs_file):
        root = parse(burp_prefs_file)
        for entry in root.iter('entry'):
            if entry.attrib["key"] == "eula{type}".format(type=product_type):
                eula_accepted = True
            if entry.attrib["key"] == "license1":
                license_activated = True
            if entry.attrib["key"] == "caCert":
                cacert_generated = True
    return eula_accepted, license_activated, cacert_generated


def check_burp_cacert_generated(prefs_file):
    """Return true if caCert entry exists in the prefs.xml file"""    
    if os.path.exists(prefs_file):
        root = parse(burp_prefs_file)
        for entry in root.iter('entry'):
            if entry.attrib["key"] == "caCert":
                return True
    return False


def find_burp_jar(burp_dir):
    """Search and return the path for the Burp Suite jar file"""
    burp_jar_path = ""
    burp_jar_files = [ f for f in os.listdir(args.burpdir) if f.startswith("burpsuite_") and f.endswith(".jar")]
    if len(burp_jar_files) > 0:
        burp_jar_path = os.path.join(args.burpdir, burp_jar_files[0])
    return burp_jar_path


def activate_burp(pexpect_child, license_file):
    """Send responses for Burp Suite activation"""
    expect_options = [
        'Do you accept the terms and conditions\\? \\(y/n\\)',
        'Do you accept the license agreement\\? \\(y/n\\)',
        'please paste your license key below.',
        'Enter preferred activation method',
        'Your license is successfully installed and activated.',
    ]
    while True:
        i = pexpect_child.expect(expect_options)
        if i == 0:
            pexpect_child.sendline('y')
            break
        elif i == 1:
            pexpect_child.sendline('y')
        elif i == 2:
            with open(license_file, 'r') as f:
                license = f.read()
                # Remove any extra spaces or new lines
                license = license.rstrip()
                pexpect_child.sendline(license)
        elif i == 3:
            pexpect_child.sendline('o')
        elif i == 4:
            break
        else:
            return False
    return True


def download_cacert(cacert_path):
    """Attempt to download public cacert"""
    with tempfile.TemporaryDirectory() as temp_cacert_dir:
        temp_cacert_path = os.path.join(temp_cacert_dir, 'cacert.der')
        while True:
            try:
                urllib.request.urlretrieve("http://localhost:8080/cert", temp_cacert_path)
                shutil.move(temp_cacert_path, cacert_path)
                os.chmod(cacert_path, 0o644)
                return True
            except urllib.error.URLError as e:
                time.sleep(10)
            except Exception as e:
                print(e)
                return False


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Burp Suite license/agreement.')
    parser.add_argument('burpdir', help='Burp Suite directory')
    parser.add_argument('--license', help='Path to Burp Suite Pro license file.')
    parser.add_argument('--cacert', help='Path to download the CA certificate to.')
    args = parser.parse_args()

    exit_status = 0
    if args.license:
        product_type = "pro"
    else:
        product_type = "community"
    
    java_path = os.path.join(args.burpdir, "jre/bin/java")
    burp_jar_path = find_burp_jar(args.burpdir)
    if not burp_jar_path:
        print('Could not find burpsuite jar file in {burpdir}'.format(burpdir=burpdir))
        sys.exit(1)
    else:
        try:
            child = pexpect.popen_spawn.PopenSpawn('{java} -Djava.awt.headless=true -jar "{jar}"'.format(java=java_path, jar=burp_jar_path), encoding='UTF-8')
            child.logfile = sys.stdout

            burp_prefs_file = os.path.join(os.path.expanduser("~"), ".java/.userPrefs/burp/prefs.xml")
            eula_accepted, license_activated, cacert_generated = check_burp_status(burp_prefs_file, product_type)
            if eula_accepted and (product_type == "community" or (product_type == "pro" and license_activated)):
                print("Burp Suite already licensed/eula accepted")
            else:
                status = activate_burp(child, args.license)
                if not status:
                    exit_status = 1
                else:
                    # Wait for Burp Suite to complete activation processes
                    while True:
                        eula_accepted, license_activated, cacert_generated = check_burp_status(burp_prefs_file, product_type)
                        if eula_accepted and (product_type == "community" or (product_type == "pro" and license_activated)) and cacert_generated:
                            break
                        time.sleep(10)

            if args.cacert:
                eula_accepted, license_activated, cacert_generated = check_burp_status(burp_prefs_file, product_type)
                if eula_accepted and (product_type == "community" or (product_type == "pro" and license_activated)) and cacert_generated:
                    downloaded = download_cacert(args.cacert)
                    if not downloaded:
                        exit_status = 1

        except Exception as e: 
            print(e)
            exit_status = 1
        finally:
            child.kill(signal.SIGTERM)

    sys.exit(exit_status)
