from odin.education.models import CheckIn


def check_macs_for_student(user, mac):
    check_ins = CheckIn.objects.filter(mac__iexact=mac)
    for check_in in check_ins:
        if not check_in.user and check_in.mac.lower() == mac.lower():
            check_in.user = user
            check_in.save()
