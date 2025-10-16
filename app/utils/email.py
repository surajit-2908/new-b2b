import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import SMTP_EMAIL, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT

def send_otp_email(to_email: str, otp: str):
    # Existing OTP email code
    subject = "Your OTP Code"
    sender = SMTP_EMAIL
    receiver = to_email

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receiver

    html_content = f"""
    <html>
      <body>
        <p>Hello,</p>
        <p>Your One-Time Password (OTP) is:</p>
        <h2 style="color:#2e6c80;">{otp}</h2>
        <p>This OTP is valid for 10 minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
        <br>
        <p>Thanks,<br>B2B System</p>
      </body>
    </html>
    """

    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(sender, receiver, message.as_string())
            print(f"OTP email sent successfully to {receiver}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise

# -----------------------
# New function: send account info email
# -----------------------
def send_user_email(to_email: str, name: str, email: str, password: str = None, action: str = "created", updated_fields: list = None):
    subject = f"Your account has been {action}"
    sender = SMTP_EMAIL
    receiver = to_email

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receiver

    if action == "created":
        html_content = f"""
        <html>
          <body>
            <p>Dear {name},</p>
            <p>Your account has been created successfully.</p>
            <p>Login details:</p>
            <ul>
              <li>Email: {email}</li>
              <li>Password: {password}</li>
            </ul>
            <p>Please keep this information safe.</p>
            <p>Login here: <a href="https://yourapp.com/login">https://yourapp.com/login</a></p>
            <br>
            <p>Thanks,<br>B2B System</p>
          </body>
        </html>
        """
    elif action == "updated":
        updated_fields_text = ", ".join(updated_fields) if updated_fields else ""
        html_content = f"""
        <html>
          <body>
            <p>Dear {name},</p>
            <p>Your account has been updated successfully.</p>
            <p>Updated fields: {updated_fields_text}</p>
            <p>Email: {email}</p>
            <p>If you did not request this change, please contact support immediately.</p>
            <br>
            <p>Thanks,<br>B2B System</p>
          </body>
        </html>
        """
    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(sender, receiver, message.as_string())
            print(f"Account email sent successfully to {receiver}")
    except Exception as e:
        print(f"Failed to send account email: {e}")
        raise
