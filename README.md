ansible-role-burpsuite
=========

Ansible role to install Burp Suite, download Jython and JRuby standalone jars, and create scripts for licensing and downloading the CA certificate.

This role also automates the licensing of Burp Suite for the specified user account.

Example Playbook
----------------

    - hosts: servers
      roles:
         - role: ansible-role-burpsuite
           burpsuite_user: hacker


License
-------

MIT
