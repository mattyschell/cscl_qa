import os
import logging
import time
import shutil


def setuplogger(loggername
               ,logname
               ,logdirectory
               ,logmode):

    # if QAing several datasets in a version we re-use the version as the log
    #   geodatabase-scripts\logs\qa-abcworkversion.log
    # otherwise 
    #   geodatabase-scripts\logs\qa-borough-DEFAULT.log
    # the notification script will stash these with unique names when QA 
    #   qa-abcworkversion-20251218-150305.log

    targetlog = os.path.join(logdirectory 
                            ,'{0}.log'.format(logname))

    logger = logging.getLogger(loggername)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(targetlog, mode=logmode)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

def getlogfile(logdir
              ,logname):

    # we likely are here because we are notifying of QA 
    # this is the flow from the .bat file
    # all logs are named consistently from setuplogger above
    # get XX.YY.log from a log directory
    # copy the log to XX.YY-20251225-160745.log so we have a trail
    # future runs will overwrite the original qa-abcversion.log

    latest_log = os.path.join(logdir
                             ,'{0}.log'.format(logname))

    with open(os.path.join(logdir, latest_log), 'r') as file:
        loglines = file.read()

    stashlog = os.path.join(logdir 
                           ,'{0}-{1}.log'.format(logname
                                                ,time.strftime("%Y%m%d-%H%M%S")
                                                ))
    shutil.copy(latest_log
               ,stashlog)

    return loglines