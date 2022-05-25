# Ansible role: Burp Suite

[![CI](https://github.com/iesplin/ansible-role-burpsuite/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/iesplin/ansible-role-burpsuite/actions/workflows/ci.yml)

Ansible role to install Burp Suite for Linux.

In addition, this role will also:

- Activate Burp Suite for the specified user (agree to terms, perform license activation)
- Save the generated PortSwigger CA certificate
- Download Jython and JRuby standalone jars
- Set a basic user profile with the Jython and JRuby jars paths 

## Requirements

This role requires the `jmespath` Python library to be present on the host running the playbook for `json_query` filters.

## Example playbooks

### Burp Suite Community edition

```yaml
- hosts: localhost

  vars:
    burpsuite_user: hacker

  roles:
    - iesplin.burp_suite
```

### Burp Suite Professional

```yaml
- hosts: localhost

  vars:
    burpsuite_user: hacker
    burpsuite_edition: pro
    burpsuite_pro_license_key: <LICENSE_KEY_STRING>

  roles:
    - iesplin.burp_suite
```

## License

MIT

## Thanks

[Jeff Geerling](https://github.com/geerlingguy) for his excellent work and Ansible roles that served as a guide for this role.