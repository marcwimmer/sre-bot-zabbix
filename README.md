# sre-bot-zabbix

Uses zabbix-sender protocol to send values (char, int, float)
to trapped zabbix-items.
Automatically sets hosts in zabbix and adds trapped items, that can be filled.

# Zabbix Version 6 incompatibility

It seems that py-zabbix uses for login the field 'user' instead of now 'username'.
I patched the py-zabbix on the production machine at the moment and wait for update on pyzabbix.

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
