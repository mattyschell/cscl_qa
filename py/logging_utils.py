import os
import logging

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