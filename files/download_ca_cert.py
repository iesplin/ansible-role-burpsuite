import argparse
import filecmp
import os
import pexpect.popen_spawn
import shutil
import signal
import sys
import tempfile
import urllib.request

parser = argparse.ArgumentParser(description='Download the Burp Suite CA Certificate.')
parser.add_argument('product', choices=['community','pro'], help='Burp Suite product type.')
parser.add_argument('burpdir', help='Burp Suite directory')
parser.add_argument('cacert', help='Path to download the CA certificate to.')
args = parser.parse_args()

java_path = os.path.join(args.burpdir, "jre/bin/java")
jar_path = os.path.join(args.burpdir, "burpsuite_{product}.jar".format(product=args.product))
cacert_file = args.cacert

exit_status = 0

try:
    child = pexpect.popen_spawn.PopenSpawn('{java} -Djava.awt.headless=true -jar "{jar}"'.format(java=java_path, jar=jar_path), encoding='UTF-8')
    child.logfile = sys.stdout
    child.expect('Proxy service started')

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_cacert_file = os.path.join(tmp_dir_name, "ca.der")
        urllib.request.urlretrieve("http://localhost:8080/cert", tmp_cacert_file)

        if os.path.exists(cacert_file):
            if filecmp.cmp(cacert_file, tmp_cacert_file):
                print("No changes to CA certificate.")
            else:
                shutil.move(tmp_cacert_file, cacert_file)
                os.chmod(cacert_file, 0o644)
                print("CA certificate updated.")
        else:
            shutil.move(tmp_cacert_file, cacert_file)
            os.chmod(cacert_file, 0o644)
            print("CA certificate saved.")

except Exception as e: 
    print(e)
    exit_status = 1
finally:
    child.kill(signal.SIGTERM)

sys.exit(exit_status)
