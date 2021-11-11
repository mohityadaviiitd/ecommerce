from django.contrib.auth.tokens import PasswordResetTokenGenerator

# import os
# from twilio.rest import Client
# ekey='AC5bd363891d716ab5255d25933293aa19'
# etoken='82c0c60979ce8abf0a7ca62a2b8a589a'
# client=Client(ekey,etoken )
# def send_sms(user_code, phone_number):
#     message=client.messages.create(body=f'Your eshop login code is {user_code}',
#     from_='+17698889177',to='+919643928187')
#     # to=f'{phone_number}')





class Generator(PasswordResetTokenGenerator):
    def _make_hash_value(self, u, timestamp):
        return str(u.pk) + str(timestamp)
maketoken=Generator()