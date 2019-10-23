import argparse
import os
import pexpect.popen_spawn
import signal
import sys

exit_status = 0

parser = argparse.ArgumentParser(description='Burp Suite license/agreement.')
parser.add_argument('burpdir', help='Burp Suite directory')
parser.add_argument('--license', help='Path to Burp Suite Pro license file.')
args = parser.parse_args()

java_path = os.path.join(args.burpdir, "jre/bin/java")
license_file = args.license

expect_options = [
    'Do you accept the terms and conditions\\? \\(y/n\\)',
    'Do you accept the license agreement\\? \\(y/n\\)',
    'please paste your license key below.',
    'Enter preferred activation method',
    'Your license is successfully installed and activated.',
    'Proxy service started'
    ]

burp_jar_files = [ f for f in os.listdir(args.burpdir) if f.startswith("burpsuite_") and f.endswith(".jar")]

if len(burp_jar_files) == 0:
    print('Could not find burpsuite jar file in {burpdir}'.format(burpdir=burpdir))
    exit_status = 1    
else:
    try:
        child = pexpect.popen_spawn.PopenSpawn('{java} -Djava.awt.headless=true -jar "{jar}"'.format(java=java_path, jar=burp_jar_files[0]), encoding='UTF-8')
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
                child.sendline(license)
            elif i == 3:
                child.sendline('o')
            elif i == 4:
                print('License successfully installed and activated.')
                break
            elif i == 5:
                print('License previously activated.')
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
