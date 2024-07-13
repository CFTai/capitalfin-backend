import uuid

from . import models


# provide retry 5 times while generate new member number
# member number with 8 digits random numbers
def generate_member_number():
    username = 0
    tried = 0
    while True and tried < 5:
        username = int(f"{str(uuid.uuid4().int)[:8]}")
        _count = models.User.objects.filter(username=username).count()
        if _count == 0:
            break
        tried += 1
    return username
