# Changelog

## 2022.12.23

- Fixed: queries for selecting latest release
- Updated: JRuby and Jython versions

## 2022.05.25

- Changed: Refactored role. Some variables have been renamed and may break existing playbooks.
- Added: Support for additional Linux distributions
- Added: GitHub Actions workflow for testing with Molecule

## 2021.07.19

- Changed: License key is now provided by value instead of a file.
- Changed: Activation, download CA public cert, and download jar tasks are standard tasks
- Added: Playbook for Molecule verification

## 2021.07.12

- Changed: Identify and download the latest Burp Suite installer version
- Changed: Merged activation and download CA public certificate scripts
- Changed: Default installation to the user's home directory so Burp can perform automatic updates.
