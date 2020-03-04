import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from defusedxml.ElementTree import parse


def is_burp_cert_generated():
    burp_prefs_file = os.path.join(os.path.expanduser("~"), ".java/.userPrefs/burp/prefs.xml")
    if not os.path.exists(burp_prefs_file):
        print('[!] Could not find {prefs_file}'.format(prefs_file=burp_prefs_file))
    else:
        for attempt in range(20):
            root = parse(burp_prefs_file)
            for entry in root.iter('entry'):
                if entry.attrib["key"] == "caCert":
                    print('[+] Burp has a CA certificate')
                    return True
            print('[-] Waiting for Burp to generate its CA certificate... {a}'.format(a=attempt))
            time.sleep(5)
        print('[!] Burp CA certificate was not generated')
        return False


exit_status = 1
retry = 5
delay = 10

parser = argparse.ArgumentParser(description='Download the Burp Suite CA Certificate.')
parser.add_argument('burpdir', help='Burp Suite directory')
parser.add_argument('cacert', help='Path to download the CA certificate to.')
args = parser.parse_args()

java_path = os.path.join(args.burpdir, "jre/bin/java")
cacert_file = args.cacert

burp_jar_files = [ f for f in os.listdir(args.burpdir) if f.startswith("burpsuite_") and f.endswith(".jar")]

if len(burp_jar_files) == 0:
    print('[!] Could not find burpsuite jar file in {burpdir}'.format(burpdir=burpdir))
else:
    burp_jar_path = os.path.join(args.burpdir, burp_jar_files[0])
    burp_args = [java_path, "-Djava.awt.headless=true", "-jar", burp_jar_path]
    with subprocess.Popen(burp_args,stderr=subprocess.DEVNULL) as proc:

        # Wait for Burp to generate and save its CA cert
        if is_burp_cert_generated():
            with tempfile.TemporaryDirectory() as temp_cacert_dir:
                temp_cacert_file = os.path.join(temp_cacert_dir, 'cacert.der')
                cacert_downloaded = False
                for attempt in range(retry):
                    print('[-] Attempting to download CA certificate')
                    try:
                        urllib.request.urlretrieve("http://localhost:8080/cert", temp_cacert_file)
                        shutil.move(temp_cacert_file, cacert_file)
                        os.chmod(cacert_file, 0o644)
                        print("[+] CA certificate saved")
                        exit_status = 0
                        break
                    except urllib.error.URLError as e:
                        time.sleep(delay)
        proc.kill()

sys.exit(exit_status)