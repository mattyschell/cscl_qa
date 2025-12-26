import os
import time
import sys
import logging
import argparse
import arcpy

from logging_utils import setuplogger
import cscl_dataset

def empty_to_none(value):
    return None if value == "" else value

def none_to_null(value):
    return 'NULL' if value is None else value

def main():

    parser = argparse.ArgumentParser(description="QA a CSCL dataset")

    # Required arguments
    parser.add_argument("dataset", help="Dataset name in cscl")
    parser.add_argument("geodatabase", help="Path to the cscl geodatabase version")
    parser.add_argument("logdir", help="Folder for logs")
    parser.add_argument("logname", help="Name of log")
    parser.add_argument("logmode", help="w(rite) or a(ppend)")
    parser.add_argument("badattribute"
                       ,help="Known junk value (ex junk, JUNK) Case insensitive."
                       ,type=empty_to_none)
    parser.add_argument("badattributecolumn", help="Column to check for junk")

    args = parser.parse_args()

    gdbversion = (
    arcpy.Describe(args.geodatabase)
         .connectionProperties
         .version
         .split('.')[-1]
    )

    setuplogger('qa_one_dataset'
               ,args.logname
               ,args.logdir
               ,args.logmode)
    logger = logging.getLogger('qa_one_dataset')

    logger.info('starting qa of {0} {1}'.format(args.dataset
                                               ,args.badattributecolumn))

    cscldataset = cscl_dataset.CSCLDataset(args.dataset)
    badkount    = 0

    if cscldataset.attribute_exists(args.geodatabase
                                   ,args.badattributecolumn
                                   ,args.badattribute):
        badkount +=1
        logger.warning(
            'QA: bad value {0} in {1} checking version {2}'.format(
                none_to_null(args.badattribute)
               ,args.badattributecolumn
               ,gdbversion
               )
            )  
    else:
        logger.info(
            'PASS: no value {0} in {1} checking version {2}'.format(
                none_to_null(args.badattribute)
               ,args.badattributecolumn
               ,gdbversion
               )
            ) 
    sys.exit(badkount)

if __name__ == '__main__':
    main()