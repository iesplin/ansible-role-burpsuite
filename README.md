ansible-role-burpsuite
=========

Ansible role to install Burp Suite.

This role by default will download and install the latest version of Burp Suite Community/Pro.

Additional tasks are performed to:

- Activate Burp Suite for the specified user (agree to terms, perform license activation)
- Download the public certificate for generated PortSwigger CA
- Download Jython and JRuby standalone jars
- Set a basic user profile with the Jython and JRuby jars

Example Playbook
----------------

    - hosts: localhost
      roles:
         - role: ansible-role-burpsuite
           burpsuite_user: hacker
           burpsuite_license_key: <LICENSE_KEY_STRING>

License
-------

MIT
