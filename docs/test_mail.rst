How to test mail
======================================================================

Open the django shell
----------------------------------------------------------------------

Check if django is taking the right method for sending the mails

    ::

        from allauth.account.adapter import get_adapter
        adapter = get_adapter()
        print(adapter.send_email_confirmation.__module__)  # Should be 'myapp.utils' if your function is used


    ::

        from allauth.account.models import EmailConfirmation, EmailAddress
        from scaleos.core.tasks import send_custom_templated_email

        user = User.objects.first()
        email_address = EmailAddress.objects.get(user=user, primary=True)
        email_confirmation = EmailConfirmation.create(email_address)

        print("User email:", email_address)
        print("Is verified:", email_address.verified)
        print("Can send confirmation:", not email_address.verified if email_address else "No email found")

        email_confirmation.send(None, email_confirmation)  # Manually trigger email sending from ALL AUTH
        send_custom_templated_email(None, email_confirmation) # If you want explicit to test your function
        

        from allauth.account.utils import send_email_confirmation
        from allauth.account.models import EmailAddress

        user_email = EmailAddress.objects.filter(user=user).first()




        email_confirmation.send(request=None)  # Manually trigger email sending from ALL AUTH