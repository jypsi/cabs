import requests

from django.conf import settings


def send_sms(mobiles, message):
    resp = requests.get(
        'https://control.msg91.com/api/sendhttp.php',
        params={
            'authkey': settings.MSG91_AUTHKEY,
            'mobiles': ','.join(mobiles),
            'message': message,
            'sender': settings.MSG91_SENDER_ID,
            'route': settings.MSG91_ROUTE_ID
        })
    assert resp.status_code == 200
