import re

from django.core.exceptions import ValidationError


def validate_mac(mac):
    regex = re.compile(r'^([0-9a-f]{2}[:]){5}([0-9a-f]{2})$', re.IGNORECASE)
    if re.match(regex, mac):
        return

    raise ValidationError(f'{mac} is not a valid mac address', 'invalid_mac_address')
