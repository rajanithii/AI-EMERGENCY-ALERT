import os
import smtplib
from email.message import EmailMessage


def _load_env_fallback():
    """Simple .env fallback: looks for .env in project root or package root and loads EMAIL_* vars."""
    candidates = [
        os.path.join(os.path.dirname(__file__), '.env'),
        os.path.join(os.path.dirname(__file__), '..', '.env'),
        os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
    ]
    for path in candidates:
        try:
            if os.path.isfile(path):
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#') or '=' not in line:
                            continue
                        k, v = line.split('=', 1)
                        k = k.strip(); v = v.strip().strip('"').strip("'")
                        if k in ('EMAIL_ADDRESS', 'EMAIL_PASSWORD') and not os.getenv(k):
                            os.environ[k] = v
                return
        except Exception:
            continue


_load_env_fallback()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS') or ""
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD') or ""


def send_otp_email(to_email: str, otp: str):
    """Send OTP to given email. Raises RuntimeError on missing config or Exception on SMTP failures."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise RuntimeError(
            "Email credentials not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD as environment variables or create a .env file."
        )

    msg = EmailMessage()
    msg["Subject"] = "LifeLine OTP Verification"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(f"Your LifeLine OTP is: {otp}")

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    try:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        # Common: Gmail app password / account access issue
        raise RuntimeError(
            "SMTP authentication failed. For Gmail, ensure 2FA is enabled and use an App Password (https://support.google.com/accounts/answer/185833)."
        ) from e
    finally:
        try:
            server.quit()
        except Exception:
            pass

    return True


def print_gmail_setup_instructions():
    msg = """
Gmail SMTP setup steps (summary):

1) Enable 2-Step Verification for your Google account:
   - https://myaccount.google.com/security -> "2-Step Verification"

2) Create an App Password (choose "Mail") and copy the 16-character app password:
   - https://myaccount.google.com/apppasswords

3) Provide credentials to this app either via environment vars or a .env file.
   - PowerShell (temporary for session):
       $Env:EMAIL_ADDRESS = "your@gmail.com"
       $Env:EMAIL_PASSWORD = "your_16_char_app_password"
   - .env file (create in project root or backend/):
       EMAIL_ADDRESS=your@gmail.com
       EMAIL_PASSWORD=your_16_char_app_password

4) Restart the FastAPI server and try signup again.

This helper can also write a .env file for you.
"""
    print(msg)


def write_env_file(path='.env', email=None, password=None):
    """Write a simple .env file with provided email and password values.

    WARNING: Storing credentials in plaintext files has security implications.
    Prefer environment variables or a secrets manager in production.
    """
    contents = []
    contents.append('# LifeLine email configuration')
    contents.append('# For Gmail use an App Password (see instructions)')
    contents.append(f'EMAIL_ADDRESS={email or "your@gmail.com"}')
    contents.append(f'EMAIL_PASSWORD={password or "your_app_password_here"}')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(contents) + '\n')
    print(f"Wrote {path} (inspect and update values as needed)")


if __name__ == '__main__':
    # Run interactive helper from the command line if invoked directly
    print('\n== LifeLine Email Setup Helper ==')
    if EMAIL_ADDRESS and EMAIL_PASSWORD:
        print('Credentials are already loaded from environment variables.')
        print('EMAIL_ADDRESS=', EMAIL_ADDRESS)
        print('If you want to overwrite/create a .env file, answer below.')
    else:
        print('No credentials detected in environment.')

    print('\nChoose an option:')
    print('  1) Show Gmail setup instructions')
    print('  2) Create a .env file with values you enter')
    print('  3) Exit')
    try:
        choice = input('Enter 1/2/3 > ').strip()
    except Exception:
        choice = '3'

    if choice == '1':
        print_gmail_setup_instructions()
    elif choice == '2':
        e = input('Enter EMAIL_ADDRESS (your@gmail.com) > ').strip()
        p = input('Enter EMAIL_PASSWORD (app password) > ').strip()
        if not e or not p:
            print('Email and password required; aborting.')
        else:
            target = '.env'
            write_env_file(target, email=e, password=p)
            print('\nCreated .env. Restart your server after updating values.')
    else:
        print('Exit')