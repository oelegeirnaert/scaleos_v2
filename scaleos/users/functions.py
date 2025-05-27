from scaleos.users.models import User


def get_user_from_mail(email_address):
    return User.objects.filter(email=email_address).first()
