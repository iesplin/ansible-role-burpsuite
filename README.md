ansible-role-burpsuite
=========

Ansible role to install Burp Suite. Includes tasks to automatically activate Burp Suite, download the CA public certificate, and download Jython and JRuby standalone jars.

This role also automates the licensing of Burp Suite for the specified user account.

Example Playbook
----------------

    - hosts: localhost
      roles:
         - role: ansible-role-burpsuite
           burpsuite_user: hacker


License
-------

MIT
