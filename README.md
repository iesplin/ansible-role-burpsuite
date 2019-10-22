ansible-role-burpsuite
=========

Ansible role to install Burp Suite, download Jython and JRuby standalone jars, and create scripts for licensing and downloading the CA certificate.

This role does not license Burp Suite as that is to be performed as a normal user account.

```yaml
- name: Accept Burp Suite license agreement/terms and conditions
  command: "python3 license_burp.py --license '{{ burpsuite_license_path }}' {{ burpsuite_dir }}"
  args:
    chdir: "{{ burpsuite_extras_dir }}"
  register: license_burp
  changed_when: "'Terms and conditions accepted.' in license_burp.stdout or
    'License successfully installed and activated.' in license_burp.stdout"

- name: Download CA certificate
  command: "python3 download_ca_cert.py {{ burpsuite_dir }} {{ burpsuite_cacert_path }}"
  args:
    chdir: "{{ burpsuite_extras_dir }}"

```

Example Playbook
----------------

    - hosts: servers
      roles:
         - ansible-role-burpsuite


License
-------

MIT
