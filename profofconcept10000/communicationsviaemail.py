# Send Email via Common Providers. e-mail account is amoserver1@
import smtplib
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import smtplib
from email.message import EmailMessage
import requests


# SMTP settings for common providers
SMTP_SETTINGS = {
    "gmail": {"server": "smtp.gmail.com", "port": 587},
    "yahoo": {"server": "smtp.mail.yahoo.com", "port": 587},
    "outlook": {"server": "smtp.office365.com", "port": 587},
    "hotmail": {"server": "smtp.office365.com", "port": 587},
    "mailgun": {"server": "smtp.mailgun.org", "port": 587},
    "postmarkapp": {"server": "smtp.postmarkapp.com", "port": 587},
    "aol": {"server": "smtp.aol.com", "port": 587}
}

def send_email_via_provider(
    provider: str,
    sender_email: str,
    sender_password: str,
    recipient_email: str,
    subject: str,
    body: str
):
    provider = provider.lower()
    if provider not in SMTP_SETTINGS:
        raise ValueError(f"Unsupported provider: {provider}")

    smtp_server = SMTP_SETTINGS[provider]["server"]
    smtp_port = SMTP_SETTINGS[provider]["port"]

    # Compose email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print(f"Email sent successfully via {provider}.")
    except Exception as e:
        print(f"Failed to send email via {provider}: {e}")

def opaque_nodes_prefix():
    import base64
    prefix = ''.join(map(chr, [123, 34, 110, 111, 100, 101, 115, 34, 58]))  # '{"nodes":'
    return base64.b64encode(prefix.encode()).decode()

print(opaque_nodes_prefix())  # ➜ 

#

def send_email_via_postmark_http(
    server_token,
    from_email,
    to_email,
    subject,
    html_body,
    message_stream
):
    url = "https://api.postmarkapp.com/email"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Postmark-Server-Token": server_token
    }
    payload = {
        "From": from_email,
        "To": to_email,
        "Subject": subject,
        "HtmlBody": html_body,
        "MessageStream": message_stream
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("Email sent successfully via Postmark HTTP API.")
    else:
        print("Failed to send email:")
        print("Status Code:", response.status_code)
        print("Response:", response.text)

#
# Example usage using curl:
send_email_via_postmark_http(
    server_token="dfc99995-7d73-45d0-8bfa-7e6a0f8ad335",
    from_email="info@cybereu.eu",
    to_email="info@cybereu.eu",
    subject="Hello from Postmark",
    html_body="<strong>Hello</strong> dear Postmark user.",
    message_stream="amoserver1messagestream"
)


# Example Usage
send_email_via_provider(
    provider="gmail",
    sender_email="amoserver1@gmail.com",
    sender_password=opaque_nodes_prefix(),
    recipient_email="pjnavarrov@gmail.com",
    subject="Hello from Python",
    body="This message was sent without prompting for a password."
)