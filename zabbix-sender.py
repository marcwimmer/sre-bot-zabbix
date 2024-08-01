import arrow
import subprocess
import json
from pathlib import Path

config_file = Path("/etc/sre/zabbix.conf")
if config_file.exists():
    config = json.loads(config_file.read_text())

ip = config['url'].split(":")[1].replace("/", "")

def on_message(client, msg, value):
    hostname = msg.topic.split("/")[0]
    key = '.'.join(msg.topic.split("/")[1:])
    if isinstance(value, dict) and value.get('timestamp'):
        timestamp = arrow.get(value['timestamp']).timestamp()
        value = value['value']
        if isinstance(value, dict):
            value = value['value']
        if value in [0, False, 0.0]:
            pass
        elif not value:
            value = ''
    else:
        timestamp = None

    if isinstance(value, bytes):
        value = value.decode('utf-8')
    url = config['url']
    command = [
        "zabbix_sender",
        "-z", ip,
        '-s', hostname,
        '-k', key,
        '-o', str(value),
    ]
    subprocess.run(command, text=True, check=True, capture_output=False)
    client.logger.debug(f"Sent data to zabbix")
