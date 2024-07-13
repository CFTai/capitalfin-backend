from django.db import connection


class ReferralOperations(object):
    # Calling store procedure sp_referral_network
    def sp_referral_network(self, user_id):
        with connection.cursor() as c:
            c.callproc("sp_referral_network", [user_id])

    def sp_referral_roi_network(self, user_id):
        with connection.cursor() as c:
            c.callproc("sp_referral_roi_network", [user_id])
