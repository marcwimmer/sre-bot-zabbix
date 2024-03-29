import arrow
from pyzabbix import ZabbixMetric, ZabbixSender


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
    packet = [
        ZabbixMetric(hostname, key, value, clock=timestamp),
    ]
    result = ZabbixSender(use_config=True).send(packet)
    client.logger.debug(result)
