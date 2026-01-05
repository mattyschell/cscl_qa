import datetime
import glob
import os
import smtplib
import argparse
import time
import shutil


def ConditionalEmail():
    try:
        from email.message import EmailMessage
    except ImportError:
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        class EmailMessage(MIMEMultipart):
            def __init__(self):
                MIMEMultipart.__init__(self)

            def set_content(self, text, subtype='plain'):
                self.attach(MIMEText(text, subtype))

    return EmailMessage()


def getlogfile(logdir
              ,logtype):

    # we are here because we are notifying of QA
    # get most recent logtype* log from a log directory
    # copy the log to qa-abcversion-20251225-160745.log so we have a trail
    # future runs will overwrite the original qa-abcversion.log

    list_of_logs = glob.glob(os.path.join(logdir
                                         ,'{0}*.log'.format(logtype)))

    latest_log = max(list_of_logs, key=os.path.getctime)

    with open(os.path.join(logdir, latest_log), 'r') as file:
        loglines = file.read()

    stashlog = os.path.join(logdir 
                           ,'{0}-{1}.log'.format(logtype
                                                ,time.strftime("%Y%m%d-%H%M%S")
                                                ))
    shutil.copy(latest_log
               ,stashlog)

    return loglines


def main():
    parser = argparse.ArgumentParser(description="Send comrades notifications")

    parser.add_argument("notification",help="Subject line for the notification")
    parser.add_argument("emails",help="Comma-separated list of recipients")
    parser.add_argument("logtype",help="Log type, ex 'qa-abcworkversion'")
    parser.add_argument("logdir",help="Directory where logs are stored")
    parser.add_argument("emailfrom",help="Email address used in From: header")
    parser.add_argument("smtpfrom",help="SMTP envelope sender")
    args = parser.parse_args()
    
    msg = ConditionalEmail()

    # notification is like "QA report for important thing (stg)"
    # in this repo we only notify on QA. Do not prepend notifications 
    # with "Completed: " or other friendly words

    content  = '{0} '.format(args.notification)
    msg['Subject'] = content
    content += 'at {0} {1}'.format(datetime.datetime.now()
                                  ,os.linesep)

    if args.logtype == 'NOLOG':
        # NOLOG is args.logtype on catastrophic failures 
        content = 'FAIL. No evidence to report. Check the logs in {}'.format(args.logdir)
        msg.set_content(content) 
    else: 
        content += '\n' + getlogfile(args.logdir
                                    ,args.logtype)  
        if 'WARNING' in content or 'ERROR' in content:
            # report log details
            msg.set_content(content) 
        else:
            # we dont need the log, keep it simple
            msg.set_content('PASS. We found no evidence that the external dataset differs from CSCL.') 
    
    smtp = smtplib.SMTP(args.smtpfrom)  
    msg['From'] = args.emailfrom
    # this is headers only 
    # if a string is passed to sendmail it is treated as a list with one element!
    msg['To'] = args.emails
  
    try:
        smtp.sendmail(msg['From']
                     ,msg['To'].split(",")
                     ,msg.as_string())
    except smtplib.SMTPRecipientsRefused as e:
        print("\n notify.py - Email not sent: relaying denied.")
        print(" notify.py - This is expected from desktop environments.\n")

    smtp.quit()


if __name__ == "__main__":
    main()

