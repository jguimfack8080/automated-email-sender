import smtplib
import imaplib
import os
import argparse
from email.message import EmailMessage
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configuration of email address and password
EMAIL_ADDRESS = 'florindangueffo@gmail.com'
EMAIL_PASSWORD = 'ijjj sjmr xvxj ypnl'

# Parse arguments
parser = argparse.ArgumentParser(description="Send bulk emails with attachments.")
parser.add_argument("--attachments", required=True, help="Directory containing attachments.")
parser.add_argument("--emails", required=True, help="File containing recipient email addresses.")
parser.add_argument("--message", required=True, help="File containing the email message.")
args = parser.parse_args()

# Data directory where email and message files are located
data_dir = 'Data'

# Docs directory where attachment files are located
docs_dir = 'Docs'

# Correct paths for attachments, emails, and message files
attachments_dir = os.path.join(docs_dir, args.attachments)  # Attachments are in the 'Docs' folder
emails_file = os.path.join(data_dir, args.emails)  # Emails file is in the 'Data' folder
message_file = os.path.join(data_dir, args.message)  # Message file is in the 'Data' folder

# Check if the directory for attachments exists within the Docs folder
if not os.path.isdir(attachments_dir):
    raise FileNotFoundError(f"Attachments directory '{attachments_dir}' does not exist in Docs.")

# Check if the email file exists in the Data folder
if not os.path.isfile(emails_file):
    raise FileNotFoundError(f"Email file '{args.emails}' not found in Data.")

# Check if the message file exists in the Data folder
if not os.path.isfile(message_file):
    raise FileNotFoundError(f"Message file '{args.message}' not found in Data.")

# Create the Logs directory if it doesn't exist
log_dir = 'Logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a subdirectory with the name based on the --attachments argument
attachment_name = os.path.basename(attachments_dir)
attachment_log_dir = os.path.join(log_dir, attachment_name)
if not os.path.exists(attachment_log_dir):
    os.makedirs(attachment_log_dir)

# Name of the log file based on the --attachments argument and date/time (with .log extension)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_name = f"{attachment_name}_{timestamp}_email_log.log"
log_file_path = os.path.join(attachment_log_dir, log_file_name)

# Configure logger
logging.basicConfig(filename=log_file_path, level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# Read recipient emails from the file
try:
    with open(emails_file, 'r') as file:
        recipient_emails = [line.strip() for line in file if line.strip()]
except Exception as e:
    raise Exception(f"Error reading email file '{emails_file}': {e}")

# Read the message and extract the subject
try:
    with open(message_file, 'r') as file:
        lines = file.readlines()
        subject = lines[0].split("Betreff: ")[1].strip() if "Betreff: " in lines[0] else "No Subject"
        email_body = ''.join(lines[1:])
except Exception as e:
    raise Exception(f"Error reading message file '{message_file}': {e}")

# Check if an email has already been sent
def email_already_sent(recipient):
    try:
        with imaplib.IMAP4_SSL('imap.gmail.com') as imap:
            imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            imap.select('"[Gmail]/Sent Mail"')
            result, data = imap.search(None, f'TO "{recipient}"')
            return result == 'OK' and data[0]
    except Exception as e:
        raise Exception(f"Error checking sent emails: {e}")

# Function to send an email
def send_email(recipient):
    if email_already_sent(recipient):
        logging.info(f"Email already sent to {recipient}, skipping.")
        return None

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg.set_content(email_body)

    # Add attachments
    try:
        for attachment in os.listdir(attachments_dir):
            attachment_path = os.path.join(attachments_dir, attachment)
            with open(attachment_path, 'rb') as file:
                file_data = file.read()
                file_name = os.path.basename(attachment_path)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    except Exception as e:
        raise Exception(f"Error adding attachments for {recipient}: {e}")

    # Send the email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logging.info(f"Email successfully sent to {recipient}.")
        return recipient
    except Exception as e:
        raise Exception(f"Failed to send email to {recipient}: {e}")

# Send emails in parallel
successful_recipients = []
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(send_email, recipient): recipient for recipient in recipient_emails}
    for future in as_completed(futures):
        result = future.result()
        if result:
            successful_recipients.append(result)

# Display recipients who received the email
if successful_recipients:
    logging.info("Emails successfully sent to:")
    for recipient in successful_recipients:
        logging.info(f" - {recipient}")
    total_sent = len(successful_recipients)
    logging.info(f"Total emails sent: {total_sent}")
else:
    total_sent = 0
    logging.info("No emails were successfully sent.")

# Save the number of emails sent
logging.info(f"Emails sent: {total_sent}")

# Calculate the total number of emails sent
def get_total_emails_sent():
    try:
        total_emails = 0
        with open(log_file_path, 'r') as file:
            for line in file:
                parts = line.split(' - Emails sent: ')
                if len(parts) == 2:
                    try:
                        total_emails += int(parts[1].strip())
                    except ValueError:
                        continue
        return total_emails
    except FileNotFoundError:
        return 0

total_emails_sent = get_total_emails_sent()
logging.info(f"Total emails sent so far: {total_emails_sent}")
