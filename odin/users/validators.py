import re


def validate_mac(mac):
    regex = re.compile(r'^([0-9a-f]{2}[:]){5}([0-9a-f]{2})$', re.IGNORECASE)
    if re.match(regex, mac):
        return True

    return False
