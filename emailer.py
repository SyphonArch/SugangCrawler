from configurations import SMTP_HOST, SMTP_USER, SMTP_SSL_PORT
from smtplib import SMTP_SSL
from getpass import getpass
from email.message import EmailMessage

SMTP_PASS = getpass("Email password: ")


def send(subject, content):
    # Craft the email using email.message.EmailMessage
    from_email = SMTP_USER
    to_emails = [SMTP_USER]
    email_message = EmailMessage()
    email_message.add_header('To', ', '.join(to_emails))
    email_message.add_header('From', from_email)
    email_message.add_header('Subject', subject)
    email_message.add_header('X-Priority', '1')  # Urgency, 1 highest, 5 lowest
    email_message.set_content(content)

    # Connect, authenticate, and send mail
    smtp_server = SMTP_SSL(SMTP_HOST, port=SMTP_SSL_PORT)
    smtp_server.set_debuglevel(1)  # Show SMTP server interactions
    smtp_server.login(from_email, SMTP_PASS)
    smtp_server.sendmail(from_email, to_emails, email_message.as_bytes())

    # Disconnect
    smtp_server.quit()


if __name__ == '__main__':
    send('Test email with subject', 'also has content')
