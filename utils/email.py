import smtplib
from email.mime.text import MIMEText
from flask import current_app

def send_email(receiver_email, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = current_app.config["SENDER_EMAIL"]
    msg["To"] = receiver_email

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(
        current_app.config["SENDER_EMAIL"],
        current_app.config["APP_PASSWORD"]
    )
    server.send_message(msg)
    server.quit()

def send_email_to_host(user_email, approve_link, file_path):
    import os

    
    file_category = os.path.dirname(file_path).split("/")[-1]
    file_category = file_category.replace("_", " ").title()

  
    file_name = os.path.basename(file_path)
    file_name = file_name.replace("_", " ").title()

    body = f"""
New download request:

User: {user_email}
Category: {file_category}
File: {file_name}

Approve here:
{approve_link}
"""

    send_email(
        current_app.config["HOST_EMAIL"],
        "New Download Request",
        body
    )