import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_email(recipient_email, subject, body):
    """
    Sends an email using the credentials stored in the .env file.
    """
    sender_email = os.getenv("INFO_EMAIL")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        raise RuntimeError("Email credentials not found in environment variables.")

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Attach the body to the email
    message.attach(MIMEText(body, "plain"))

    try:
        # For most professional emails (including .co.uk), we use SMTP.
        # Assuming standard Gmail/Outlook style SMTP. 
        # You may need to adjust the host/port depending on the provider.
        # Common providers like Outlook/Office365 use smtp.office365.com:587
        # Gmail uses smtp.gmail.com:587
        
        # Attempting connection to a common professional mail server (SMTP)
        # If the domain is custom, the provider usually handles the relay.
        # We'll start with a generic approach or you can specify the SMTP server.
        
        # Since it's a .co.uk domain, it's likely hosted via a professional provider.
        # For now, we'll try a standard setup and provide an easy way to change the host.
        smtp_server = "smtp.office365.com" # Common for professional .co.uk domains
        smtp_port = 587

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
