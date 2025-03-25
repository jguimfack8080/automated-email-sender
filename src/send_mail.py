import smtplib
import imaplib
import os
import argparse
from email.message import EmailMessage
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging - No console output, only file logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)-8s - %(message)s', handlers=[])
logger = logging.getLogger(__name__)

def setup_file_logging(log_file_path):
    """Setup file logging with the specified path"""
    logger.handlers = []  # Clear existing handlers
    file_handler = logging.FileHandler(log_file_path, mode='w')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def read_email_credentials(attachments_dir):
    """Read email credentials from credentials.txt file"""
    try:
        credentials_dir = os.path.join('Docs', attachments_dir, 'credentials')
        credentials_file = os.path.join(credentials_dir, 'credentials.txt')

        if not os.path.isfile(credentials_file):
            raise FileNotFoundError(f"Credentials file not found at {credentials_file}")

        with open(credentials_file, 'r') as file:
            credentials = file.readlines()
            if len(credentials) < 2:
                raise ValueError("Credentials file must contain email and password on separate lines")
            return credentials[0].strip(), credentials[1].strip()
    except Exception as e:
        logger.error("❌ Error reading credentials: %s", str(e))
        raise

def email_already_sent(recipient, email, password):
    """Check if email was already sent to recipient"""
    try:
        with imaplib.IMAP4_SSL('imap.gmail.com') as imap:
            imap.login(email, password)
            imap.select('"[Gmail]/Sent Mail"')
            result, data = imap.search(None, f'TO "{recipient}"')
            return result == 'OK' and data[0]
    except Exception as e:
        logger.error("⚠️ Error checking sent emails for %s: %s", recipient, str(e))
        return False

def send_email(recipient, email, password, subject, body, attachments_dir, args):
    """Send email to single recipient with error handling"""
    try:
        if email_already_sent(recipient, email, password):
            logger.debug("⏩ Already sent to %s - skipping", recipient)
            return None

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = email
        msg['To'] = recipient
        msg.set_content(body)

        # Add attachments
        for attachment in os.listdir(attachments_dir):
            attachment_path = os.path.join(attachments_dir, attachment)
            if "credentials" in attachment_path:
                continue
            
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=attachment)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email, password)
            smtp.send_message(msg)
        
        logger.info("✔ Successfully sent to %s", recipient)
        return recipient
    except Exception as e:
        logger.error("✖ Failed to send to %s: %s", recipient, str(e))
        return None

def log_email_summary(successful_recipients, all_recipients):
    """Log a detailed summary of email sending results"""
    logger.info("\n" + "="*60)
    logger.info("📧 EMAIL SENDING SUMMARY REPORT (CURRENT SESSION)")
    logger.info("="*60)

    if successful_recipients:
        logger.info("\n✅ SUCCESSFUL DELIVERIES (%d):", len(successful_recipients))
        for idx, email in enumerate(successful_recipients, 1):
            logger.info("   %03d. %s", idx, email)
    else:
        logger.warning("\n⚠️ NO SUCCESSFUL DELIVERIES IN THIS SESSION")

    failed_count = len(all_recipients) - len(successful_recipients)
    success_rate = (len(successful_recipients) / len(all_recipients)) * 100 if all_recipients else 0

    logger.info("\n📊 SESSION STATISTICS:")
    logger.info("   Total recipients processed: %4d", len(all_recipients))
    logger.info("   Successfully sent:         %4d (%.1f%%)", len(successful_recipients), success_rate)
    logger.info("   Failed/skipped:            %4d", failed_count)
    logger.info("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Send bulk emails with attachments.")
    parser.add_argument("--attachments", required=True, help="Directory containing attachments")
    parser.add_argument("--emails", required=True, help="File containing recipient emails")
    parser.add_argument("--message", required=True, help="File containing email message")
    args = parser.parse_args()

    # Create log directory structure
    log_base_dir = 'Logs'
    attachment_log_dir = os.path.join(log_base_dir, args.attachments)
    os.makedirs(attachment_log_dir, exist_ok=True)  # Create directory if not exists

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_name = f"session_{timestamp}.log"
    log_file_path = os.path.join(attachment_log_dir, log_file_name)

    setup_file_logging(log_file_path)

    logger.info("🚀 PROGRAM START - NEW SESSION")
    logger.info("="*60 + "\n")
    logger.info("📁 Log directory: %s", attachment_log_dir)

    data_dir = 'Data'
    docs_dir = 'Docs'
    attachments_dir = os.path.join(docs_dir, args.attachments)
    emails_file = os.path.join(data_dir, args.emails)
    message_file = os.path.join(data_dir, args.message)

    if not os.path.isdir(attachments_dir):
        raise FileNotFoundError(f"Attachments directory not found: {attachments_dir}")
    if not os.path.isfile(emails_file):
        raise FileNotFoundError(f"Emails file not found: {emails_file}")
    if not os.path.isfile(message_file):
        raise FileNotFoundError(f"Message file not found: {message_file}")

    email, password = read_email_credentials(args.attachments)
    logger.info("🔑 Using email account: %s", email)

    with open(emails_file, 'r') as f:
        recipients = [line.strip() for line in f if line.strip()]
    logger.info("📩 Loaded %d recipient emails", len(recipients))

    with open(message_file, 'r') as f:
        lines = f.readlines()
        subject = lines[0].split("Betreff: ")[1].strip() if "Betreff: " in lines[0] else "No Subject"
        body = ''.join(lines[1:])
    logger.info("✉️ Email subject: '%s'", subject)

    attachments = [f for f in os.listdir(attachments_dir) if not f.startswith('credentials')]
    logger.info("📎 Attachments (%d): %s", len(attachments), ", ".join(attachments))

    successful = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(send_email, recipient, email, password, subject, body, attachments_dir, args): recipient for recipient in recipients}

        for future in as_completed(futures):
            result = future.result()
            if result:
                successful.append(result)

    log_email_summary(successful, recipients)

    logger.info("🏁 PROGRAM END")
    return 0

if __name__ == "__main__":
    exit(main())