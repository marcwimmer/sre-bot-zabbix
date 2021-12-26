import arrow
from pyzabbix.api import ZabbixAPI
import json
from pathlib import Path
import inspect
import os
from pathlib import Path
current_dir = Path(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))

replace_chars = (current_dir / 'replace_chars.txt').read_text().strip()

config_file = Path("/etc/sre/zabbix.conf")
if config_file.exists():
    config = json.loads(config_file.read_text())

def install(parent_path):
    if not config_file.exists():
        config_file.write_text(json.dumps({
            'url': 'http://localhost:8080',
            'user': 'Admin',
            'password': 'zabbix'
        }))

def _get_hosts(zapi, hostname):
    hosts = zapi.do_request('host.get', {
        "filter": {
            "host": [
                hostname,
            ]
        }
    })
    return hosts['result']

def _create_host(zapi, hostname):
    info = {
        'host': hostname,
        "groups": [
            {
                "groupid": "4"
            }
        ],
        "tags": [
            {
                "tag": "Host name",
                "value": "Linux server"
            }
        ],
        "inventory_mode": 0,
    }
    res = zapi.do_request('host.create', info)
    host_id = res['result']['hostids'][0]
    return host_id

def _get_application(zapi, hostid, application_name):
    res = zapi.do_request('application.get', {
        "hostids": hostid,
        "output": "extend",
        "filter": {
            "name": application_name,
        }
    })
    return list(map(lambda x: x['applicationid'], res['result']))

def _get_item(zapi, hostid, item_key):
    res = zapi.do_request('item.get', {
        "hostids": hostid,
        "output": "extend",
        "search": {
            "key_": item_key,
        },
    })
    return res['result']

def _create_item(zapi, hostid, item_key, name, ttype, applications):
    value_type = {
        'char': 1,
        'float': 0,
        'int': 3,
        'log': 2,
        'text': 4,
    }[ttype]

    res = zapi.do_request('item.create', {
        "name": item_key,
        "key_": item_key,
        "hostid": hostid,
        "type": 2, # Zabbix trapper to enable zabbix-send
        "value_type": value_type,
        "delay": "1s",
        "applications": applications,
    })
    item_id = res['result']['itemids'][0]
    return item_id

def _create_application(zapi, hostid, name):
    res = zapi.do_request('application.create', {
        "name": name,
        "hostid": hostid,
    })
    return res['result']['applicationids']

def on_message(client, msg, value):
    hostname = msg.topic.split("/")[0]
    key = '.'.join(msg.topic.split("/")[1:])
    for c in replace_chars:
        key = key.replace(c, "_")

    last_update_info = Path('/tmp/zabbix_adapter_last_updates') / key
    last_update_info.parent.mkdir(exist_ok=True)
    try:
        last_update = arrow.get(last_update_info.read_text())
    except Exception:
        last_update = arrow.get("1980-04-04")

    if (arrow.get() - last_update).total_seconds() < 60:
        return

    with ZabbixAPI(url=config['url'], user=config['user'], password=config['password']) as zapi:
        hosts = _get_hosts(zapi, hostname)
        if not hosts:
            host_id = _create_host(zapi, hostname)
        else:
            host_id = hosts[0]['hostid']

        if isinstance(value, int):
            value = {
                'module': None,
                'value': value,
            }

        application_name = value['module']
        if application_name:
            application_ids = _get_application(zapi, host_id, application_name)
            if not application_ids:
                application_ids = _create_application(zapi, host_id, application_name)
        else:
            application_ids = []

        item = _get_item(zapi, host_id, key)
        if not item:
            value = value['value']
            try:
                value = value.decode('utf-8')
            except Exception: pass

            if isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass

            if isinstance(value, (int, bool)):
                ttype = 'int'
            elif isinstance(value, (float,)):
                ttype = 'float'
            elif len(value or '') > 256:
                ttype = 'log'
            else:
                ttype = 'char'

            _create_item(zapi, host_id, key, key, ttype, application_ids)
    last_update_info.write_text(str(arrow.get()))
