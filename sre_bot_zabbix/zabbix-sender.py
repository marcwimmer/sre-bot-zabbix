import arrow
from pyzabbix import ZabbixMetric, ZabbixSender


def on_message(client, msg, value):
    hostname = msg.topic.split("/")[0]
    key = '.'.join(msg.topic.split("/")[1:])
    if isinstance(value, dict):
        timestamp = arrow.get(value['timestamp']).timestamp()
        value = value['value'] or ''
    else:
        timestamp = None

    if isinstance(value, bytes):
        value = value.decode('utf-8')
    packet = [
        ZabbixMetric(hostname, key, value, clock=timestamp),
    ]
    result = ZabbixSender(use_config=True).send(packet)
    client.logger.debug(result)

