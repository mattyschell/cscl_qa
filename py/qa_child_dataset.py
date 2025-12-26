import os
import time
import sys
import logging
import argparse

import cscl_dataset

# This is a specific QA task for replicas
# It checks for a specific pattern that causes replication failure
# Bad temporary data gets introduced on the parent
# The bad data gets replicated to the child
# The bad data gets cleaned up in the parent and replication fails
# Interestingly replication only fails on some replicas
# Your code writer does not understand what exactly is bad about the data or 
# or why replication fails. 
# What your code writer does see in the fail state
#   1. The bad temp data is in the child only 
#   2. The parent and child dataset counts have diverged
# Prior to the fail state
#   3. The bad temp data is in parent and child
# This script checks 1 2 and 3

def setuplogger(loggername
               ,datasetname
               ,logdirectory):

    # ..geodatabase-scripts\logs\qa-borough-20250403-160745.log
    targetlog = os.path.join(logdirectory 
                            ,'qa-{0}-{1}.log'.format(
                                datasetname
                               ,time.strftime("%Y%m%d-%H%M%S")))

    logger = logging.getLogger(loggername)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(targetlog, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

def main():

    parser = argparse.ArgumentParser(description="QA a child CSCL dataset")

    parser.add_argument("dataset", help="Dataset name in cscl")
    parser.add_argument("geodatabase"
                       ,help="Path to the parent cscl geodatabase")
    parser.add_argument("childgeodatabase"
                       ,help="Path to the child cscl geodatabase")
    parser.add_argument("logdir", help="Folder for logs")
    parser.add_argument("--badattribute"
                       ,help="Known junk value (ex junk)", default=None)
    parser.add_argument("--badattributecolumn"
                       ,help="Column to check for junk", default=None)
    parser.add_argument("--deltastart"
                       ,help="Known count difference on the child", default=0)

    args = parser.parse_args()

    setuplogger('qa_child_dataset'
               ,args.dataset
               ,args.logdir)
    logger = logging.getLogger('qa_child_dataset')

    logger.info('starting qa of {0}'.format(args.dataset))
    logger.info('comparing parent geodatabase {0}'.format(args.geodatabase))
    logger.info('to child geodatabase {0}'.format(args.childgeodatabase))

    cscldataset = cscl_dataset.CSCLDataset(args.dataset)
    badkount    = 0

    if args.badattributecolumn and args.badattribute:
        if cscldataset.attribute_exists(args.geodatabase
                                       ,args.badattributecolumn
                                       ,args.badattribute):
            badkount +=1
            logger.warning(
                'QA: bad {0} value {1} on parent'.format(
                    args.badattributecolumn
                   ,args.badattribute))  
        else:
            logger.info(
                'PASS: no value {0} in {1} on parent'.format(
                    args.badattribute
                   ,args.badattributecolumn))                        

        if cscldataset.attribute_exists(args.childgeodatabase
                                       ,args.badattributecolumn
                                       ,args.badattribute):
            badkount +=1
            logger.warning(
                'QA: bad {0} value {1} on child'.format(
                    args.badattributecolumn
                   ,args.badattribute))  
        else:
            logger.info(
                'PASS: no value {0} in {1} on child'.format(
                    args.badattribute
                   ,args.badattributecolumn)) 

    try:

        if cscldataset.count(args.geodatabase) != (
            cscldataset.count(args.childgeodatabase) + args.deltastart
            ):

            badkount +=1
            logger.info(
                'Parent count returned {0}'.format(
                    cscldataset.count(args.geodatabase)))
            logger.info(
                'Child count returned {0}'.format(
                    cscldataset.count(args.childgeodatabase)))
            logger.warning(
                'QA: bad row count on {0}'.format(args.childgeodatabase))
        else:
            logger.info(
                'PASS: good row count on {0}'.format(args.childgeodatabase))
    
    except TypeError:
        logger.error('Failed to get counts')
        logger.error(
            'Parent count returned {0}'.format(
                cscldataset.count(args.geodatabase)))
        logger.error(
            'Child count returned {0}'.format(
                cscldataset.count(args.childgeodatabase)))
        raise ValueError('Failed to get counts, check the logs')

    if badkount == 0:
        logger.info(
            'PASS: summary all checks of {0} on {1}'.format(
                args.dataset
               ,args.childgeodatabase))
    else:
        logger.warning(
            'QA: summary of all checks of {0} on {1}'.format(
                args.dataset
               ,args.childgeodatabase))

    sys.exit(badkount)

if __name__ == '__main__':
    main()