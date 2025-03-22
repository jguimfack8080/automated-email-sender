# Automated Email Sender

**Project Overview**:  
`automated-email-sender` is a Python-based project designed to send bulk emails with attachments using a Gmail account. The project enables users to send emails to a list of recipients, attaching files from a specific directory, while ensuring that the email content is read from a provided message file. This project includes functionalities for logging email actions, ensuring no duplicate emails are sent, and cleaning email lists for duplicate entries.

## Project Features

- **Bulk Email Sending**: Send emails to a list of recipients with attachments.
- **Attachment Handling**: Supports adding attachments from a specified directory.
- **Message Management**: Email content (subject and body) is read from a provided text file.
- **Log Generation**: Logs every email sent (successes and failures) for tracking purposes.
- **Duplicate Email Prevention**: Ensures that emails are not sent multiple times to the same recipient.
- **Email List Cleaning**: Provides functionality to clean up and remove duplicate email addresses from a list of recipients.

## Project Structure

This project consists of the following components:

1. **`send_mail.py`**:  
   This is the core script that handles the bulk sending of emails with attachments to the recipients provided in the input file. It checks if an email has already been sent to avoid duplication, and it generates a log of email sending activity.

2. **`clean_double_mail.py`**:  
   A script that cleans up an email list by removing duplicate entries. It ensures that the recipient list is unique and sorted alphabetically, saving the cleaned list to a new file prefixed with `cleaned_`.

3. **Log Directory**:  
   The project automatically creates a `Logs` directory where logs of email sending activity are saved. The logs include timestamps and indicate whether emails were successfully sent or failed.

## Prerequisites

Before running this project, ensure the following are installed:
- Python 3.x or higher.
- Python libraries (all standard libraries):
  - `smtplib`
  - `imaplib`
  - `os`
  - `argparse`
  - `email`
  - `datetime`
  - `concurrent.futures`
  - `logging`

Additionally, you will need:
- Access to a Gmail account.
- SMTP and IMAP access credentials for the Gmail account.

## Installation

1. Clone this repository or download the Python scripts.
2. No additional dependencies need to be installed as all required libraries are part of Python's standard library.

## Usage

### Sending Emails

To send emails with attachments, run the `send_mail.py` script with the following arguments:

```bash
python send_mail.py --attachments <attachments_directory> --emails <emails_file> --message <message_file>
