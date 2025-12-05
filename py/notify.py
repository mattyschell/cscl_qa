import sys
import datetime
import glob
import os
import smtplib
import socket
from email.message import EmailMessage


def getlogfile(logdir
              ,logtype):

    # ex get most recent logtype* log from a log directory

    list_of_logs = glob.glob(os.path.join(logdir
                                         ,'*{0}*.log'.format(logtype)))

    latest_log = max(list_of_logs, key=os.path.getctime)

    with open(os.path.join(logdir, latest_log), 'r') as file:
        loglines = file.read()

    return loglines

def main():

    pnotification   = sys.argv[1] # becomes subject line 
    pemails         = sys.argv[2] 
    plogtype        = sys.argv[3] # ex 'qa-borough' 'NOLOG'
    plogdir         = sys.argv[4]
    pemailfrom      = sys.argv[5]
    psmtpfrom       = sys.argv[6]
    
    msg = EmailMessage()

    # notification is like "QA: a very important thing (stg)"
    # in this repo we only notify on QA. Do not prepend notifications 
    # with "Completed: " or other re-assuring words

    content  = '{0} '.format(pnotification)
    msg['Subject'] = content
    content += 'at {0} {1}'.format(datetime.datetime.now()
                                  ,os.linesep)

    if plogtype == 'NOLOG':
        # NOLOG is plogtype on failures 
        content = 'FAIL. No evidence to report. Check the logs in {}'.format(plogdir)
        msg.set_content(content) 
    else: 
        content += '\n' + getlogfile(plogdir
                                    ,plogtype)  
        if 'WARNING' in content:
            # report log details
            msg.set_content(content) 
        else:
            # we dont need the log, keep it simple
            msg.set_content('PASS. We found no evidence that the external dataset differs from CSCL.') 
    
    smtp = smtplib.SMTP(psmtpfrom)  
    msg['From'] = pemailfrom
    # this is headers only 
    # if a string is passed to sendmail it is treated as a list with one element!
    msg['To'] = pemails
  
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

