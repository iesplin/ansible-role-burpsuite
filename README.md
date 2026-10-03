# Ansible role: Burp Suite

[![CI](https://github.com/iesplin/ansible-role-burpsuite/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/iesplin/ansible-role-burpsuite/actions/workflows/ci.yml)

Ansible role to install Burp Suite for Linux.

Installs into the `~/BurpSuite` directory of the user running the role.
 
In addition, this role will also:

- Activate Burp Suite for the user (agree to terms, perform license activation)
- Save the generated PortSwigger CA certificate
- Download Jython and JRuby standalone jars
- Set a basic user profile with the Jython and JRuby jars paths

## Requirements

The target host must:

- Run Debian, Ubuntu or Fedora on x86_64 or aarch64, with a graphical desktop.
- Have the Python `pexpect` library installed, if `burpsuite_activate` is `true`. The role does not install it.
- Have internet access to `portswigger.net` and `repo1.maven.org`.

## Role variables

| Variable | Default | Description |
|---|---|---|
| `burpsuite_early_adopter` | `false` | Install from the Early Adopter release channel instead of Stable |
| `burpsuite_pro_license_key` | `''` | Burp Suite Professional licence key. Leave empty for Community edition |
| `burpsuite_activate` | `true` | Accept the licence agreement, activate the licence and download the CA certificate |
| `burpsuite_extras_dir` | `~/BurpSuiteExtras` | Directory for the extra jars and the activation script. Must be writable by the user |
| `burpsuite_cacert_path` | `<burpsuite_extras_dir>/PortSwigger_CA.der` | Path to save the PortSwigger CA public certificate |
| `burpsuite_extras_jars` | JRuby and Jython | Extra jars to download, each with a `jar` filename, `url` and `checksum` |

## Updates

Each run looks up the latest release on the selected channel and compares it with the installed version. Burp Suite is only installed when it is missing or the installed version differs from that release, so a run reports changes whenever a new release has come out. Switching channels also reinstalls, even to an older version.

An existing `UserConfig.json` is not replaced. Only the JRuby and Jython jar paths in it are updated.

## Choosing the user

The role installs and activates Burp Suite for whichever user it runs as. Either connect as that user, or use `become` and `become_user` on the role to run it as another user. Running the role as root installs Burp Suite for root.

## Example playbooks

### Burp Suite Community edition, for the connecting user

```yaml
- hosts: localhost

  roles:
    - iesplin.burp_suite
```

### Burp Suite Professional, for another user

```yaml
- hosts: localhost

  tasks:
    - name: Install Burp Suite Professional for hacker
      ansible.builtin.include_role:
        name: iesplin.burp_suite
        apply:
          become: true
          become_user: hacker
      vars:
        burpsuite_pro_license_key: <LICENSE_KEY_STRING>
```

## License

MIT
