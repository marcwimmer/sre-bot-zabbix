# sre-bot-zabbix

Uses zabbix-sender protocol to send values (char, int, float)
to trapped zabbix-items.
Automatically sets hosts in zabbix and adds trapped items, that can be filled.


# Configuration

```bash

``

# How to upload new version
  * increase version in setup.py
  * one time: pipenv install twine --dev
  * pipenv shell
  * python3 setup.py upload

# install directly

pip3 install git+https://github.com/marcwimmer/sre-bot`