# sre-bot-zabbix

Uses zabbix-sender protocol to send values (char, int, float)
to trapped zabbix-items.
Automatically sets hosts in zabbix and adds trapped items, that can be filled.

# Pip packages

```
pip install py-zabbix

# do not install pyzabbix
```

# Configuration

```bash

#/etc/sre/zabbix.conf
{
        "user": "autobots",
        "password": "*************",
        "url": "https://zabbix.myhost.com"
}

``
