import argparse
import os
import pexpect.popen_spawn
import signal
import sys
from defusedxml.ElementTree import parse

exit_status = 0

parser = argparse.ArgumentParser(description='Burp Suite license/agreement.')
parser.add_argument('burpdir', help='Burp Suite directory')
parser.add_argument('--license', help='Path to Burp Suite Pro license file.')
args = parser.parse_args()

product_type = "community"
if args.license:
    license_file = args.license
    product_type = "pro"

# Check if Burp Suite has already been licensed/eula accepted
burp_prefs_file = os.path.join(os.path.expanduser("~"), ".java/.userPrefs/burp/prefs.xml")
eula_accepted = False
licence_installed = False
if os.path.exists(burp_prefs_file):
    root = parse(burp_prefs_file)
    for entry in root.iter('entry'):
        if entry.attrib["key"] == "eula{type}".format(type=product_type):
            eula_accepted = True
        if entry.attrib["key"] == "license1":
            licence_installed = True

# If licensed/eula accepted, then print message
if eula_accepted and (product_type == "community" or (product_type == "pro" and licence_installed)):
    print("Burp Suite already licensed/eula accepted")
# Otherwise automate installation of license and acceptance of eula
else:
    expect_options = [
        'Do you accept the terms and conditions\\? \\(y/n\\)',
        'Do you accept the license agreement\\? \\(y/n\\)',
        'please paste your license key below.',
        'Enter preferred activation method',
        'Your license is successfully installed and activated.',
        ]

    burp_jar_files = [ f for f in os.listdir(args.burpdir) if f.startswith("burpsuite_") and f.endswith(".jar")]
    if len(burp_jar_files) == 0:
        print('Could not find burpsuite jar file in {burpdir}'.format(burpdir=burpdir))
        exit_status = 1    
    else:
        try:
            java_path = os.path.join(args.burpdir, "jre/bin/java")
            burp_jar_path = os.path.join(args.burpdir, burp_jar_files[0])
            child = pexpect.popen_spawn.PopenSpawn('{java} -Djava.awt.headless=true -jar "{jar}"'.format(java=java_path, jar=burp_jar_path), encoding='UTF-8')
            child.logfile = sys.stdout

            while True:
                i = child.expect(expect_options)
                if i == 0:
                    child.sendline('y')
                    print('Terms and conditions accepted.')
                    break
                elif i == 1:
                    child.sendline('y')
                elif i == 2:
                    with open(license_file, 'r') as f:
                        license = f.read()
                        # Remove any extra spaces or new lines
                        license = license.rstrip()
                        child.sendline(license)
                elif i == 3:
                    child.sendline('o')
                elif i == 4:
                    break
                else:
                    print('Unexpected expect!')
                    exit_status = 1
                    break

        except Exception as e: 
            print(e)
            exit_status = 1
        finally:
            child.kill(signal.SIGTERM)

sys.exit(exit_status)
