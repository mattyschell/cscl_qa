import os
import time
import sys
import logging
import argparse
import arcpy

import cscl_dataset

def setuplogger(loggername
               ,datasetname
               ,logdirectory):

    # ..geodatabase-scripts\logs\qa-borough-DEFAULT-20250403-160745.log
    targetlog = os.path.join(logdirectory 
                            ,'qa-{0}-{1}.log'.format(datasetname
                                                    ,time.strftime("%Y%m%d-%H%M%S")))

    logger = logging.getLogger(loggername)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(targetlog, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

def main():

    parser = argparse.ArgumentParser(description="QA a CSCL dataset")

    # Required arguments
    parser.add_argument("dataset", help="Dataset name in cscl")
    parser.add_argument("geodatabase", help="Path to the cscl geodatabase version")
    parser.add_argument("logdir", help="Folder for logs")
    parser.add_argument("badattribute", help="Known junk value (ex junk, JUNK) Case insensitive.")
    parser.add_argument("badattributecolumn", help="Column to check for junk")

    args = parser.parse_args()

    gdbversion = arcpy.Describe(args.geodatabase).connectionProperties.version.split('.')[-1]

    # add version to log name since qa_child_dataset.py logs use only dataset
    setuplogger('qa_dataset'
               ,'{0}-{1}'.format(args.dataset, gdbversion)
               ,args.logdir)
    logger = logging.getLogger('qa_dataset')

    logger.info('starting qa of {0} {1}'.format(args.dataset
                                               ,args.badattributecolumn))

    cscldataset = cscl_dataset.CSCLDataset(args.dataset)
    badkount    = 0

    if cscldataset.attribute_exists(args.geodatabase
                                   ,args.badattributecolumn
                                   ,args.badattribute):
        badkount +=1
        logger.warning('QA: bad {0} value {1} checking version {2}'.format(args.badattributecolumn
                                                                            ,args.badattribute
                                                                            ,gdbversion))  
    else:
        logger.info('PASS: no value {0} in {1} checking version {2}'.format(args.badattribute
                                                                            ,args.badattributecolumn
                                                                            ,gdbversion)) 

    sys.exit(badkount)

if __name__ == '__main__':
    main()