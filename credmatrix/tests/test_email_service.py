import pytest
from backend.services.email_service import send_email

@pytest.mark.django_db
def test_send_email_real():
    """Test the send_email function with Amazon SES."""
    subject = "Test Subject"
    message = "This is a test email sent via Amazon SES."
    recipient_list = ["srivaishnavsri@gmail.com"]  # Replace with a verified recipient email
    from_email = "noreply@credmatrix.ai"  # Replace with a verified sender email

    result = send_email(subject, message, recipient_list, from_email)

    assert result is True, "Failed to send email via Amazon SES"