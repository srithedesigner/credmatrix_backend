from django.core.mail import send_mail
from django.conf import settings

def send_email(subject, message, recipient_list, from_email=None):
    """
    Utility function to send an email.
    :param subject: Email subject
    :param message: Email body
    :param recipient_list: List of recipient email addresses
    :param from_email: Sender email address (optional, defaults to settings.DEFAULT_FROM_EMAIL)
    :return: None
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,  # Raise errors if email fails
        )
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    return True