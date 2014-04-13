from email.mime.text import MIMEText
import smtplib

from team_not_found.cfg import config


def send_mail(to, subject, body):
    # Create the message
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = '%s <%s>' % (config['email']['from_name'], config['email']['from_email'])
    msg['To'] = to

    #Send it
    server = smtplib.SMTP(
        config['email']['server'],
        config['email']['port']
    )
    server.ehlo()
    server.starttls()
    server.login(
        config['email']['username'],
        config['email']['password']
    )
    server.sendmail(
        config['email']['from_email'],
        [to],
        msg.as_string()
    )
    server.quit()
