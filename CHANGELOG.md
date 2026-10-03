# Changelog

All notable changes to this role are documented in this file.

## [2.0.0] - 2026-10-02

### Breaking changes

- Use the combined Burp Suite desktop installer, which covers both Professional and Community editions and always installs the latest release from the selected channel. As a result, the `burpsuite_edition`, `burpsuite_version` and `burpsuite_installer_sha256_checksum` variables have been removed.
- `burpsuite_user` has been removed. The role installs and activates Burp Suite for the user it runs as. Use `become` and `become_user` on the role to install for another user.
- `burpsuite_install_dir` has been removed. Burp Suite is always installed to `~/BurpSuite`, so the user can apply Burp Suite's own updates.
- `burpsuite_release_channel` has been replaced by the `burpsuite_early_adopter` flag. Set it to `true` to install from the Early Adopter channel, otherwise Stable is installed.
- The role no longer installs packages. Install `python3-pexpect` before running the role if `burpsuite_activate` is `true`. The fontconfig and FreeType libraries are expected to be present on a graphical desktop.

### Added

- Fail at the start of the run if any removed variable is still set.
- Fail at the start of the run if `burpsuite_activate` is `true` and the Python `pexpect` library is not installed.

### Changed

- Select the Linux x64 or ARM installer based on the CPU architecture.
- The `community.general` collection and the `jmespath` Python library are no longer required.
- Updated JRuby to 10.1.2.0.

## [1.0.5] - 2026-03-04

### Changed

- Updated JRuby to 10.0.3.0.

### Fixed

- Version lookup updated for changes to the PortSwigger releases API.

## [1.0.4] - 2025-11-19

### Changed

- Updated JRuby and Jython versions.
- Switched to podman for testing.

### Fixed

- Enforced JSON conversion for Burp release data to resolve version lookup failures.

## [1.0.3] - 2022-12-23

### Changed

- Updated JRuby and Jython versions.

### Fixed

- Queries for selecting the latest release.

## [1.0.1] - 2022-05-25

### Breaking changes

- Refactored the role. Some variables have been renamed and may break existing playbooks.

### Added

- Support for additional Linux distributions.
- GitHub Actions workflow for testing with Molecule.

## 2021-07-19 (untagged)

### Added

- Playbook for Molecule verification.

### Changed

- Licence key is now provided by value instead of a file.
- Activation, CA public certificate download and jar download are now standard tasks.

## 2021-07-12 (untagged)

### Changed

- Identify and download the latest Burp Suite installer version.
- Merged the activation and CA public certificate download scripts.
- Default installation to the user's home directory so Burp can perform automatic updates.

[2.0.0]: https://github.com/iesplin/ansible-role-burpsuite/compare/1.0.5...2.0.0
[1.0.5]: https://github.com/iesplin/ansible-role-burpsuite/compare/1.0.4...1.0.5
[1.0.4]: https://github.com/iesplin/ansible-role-burpsuite/compare/1.0.3...1.0.4
[1.0.3]: https://github.com/iesplin/ansible-role-burpsuite/compare/1.0.2...1.0.3
[1.0.1]: https://github.com/iesplin/ansible-role-burpsuite/releases/tag/1.0.1
