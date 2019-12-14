import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

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
    print('Could not find burpsuite jar file in {burpdir}'.format(burpdir=burpdir))
    exit_status = 1    
else:
    burp_jar_path = os.path.join(args.burpdir, burp_jar_files[0])
    burp_args = [java_path, "-Djava.awt.headless=true", "-jar", burp_jar_path, "--use-defaults"]
    with subprocess.Popen(burp_args) as proc:
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            for attempt in range(retry):
                try:
                    tmp_cacert_file = os.path.join(tmp_dir_name, "ca.der")
                    urllib.request.urlretrieve("http://localhost:8080/cert", tmp_cacert_file)
                    shutil.move(tmp_cacert_file, cacert_file)
                    os.chmod(cacert_file, 0o644)
                    print("CA certificate saved.")
                    exit_status = 0
                    break
                except Exception as e:
                    time.sleep(delay)
        proc.kill()

sys.exit(exit_status)