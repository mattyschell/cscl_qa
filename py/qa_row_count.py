import os
import sys
import logging
import argparse

from logging_utils import setuplogger
import cscl_dataset

# Sanity check that big datasets have not been gutted or duplicated.
# Limits are deliberately loose (roughly 90 and 110 percent of normal) so that
# only catastrophic change trips QA. Update resources/rowcountrange* as data grows.


def get_ranges(rangefile):

    ranges = []
    with open(rangefile) as l:
        for line in l:
            if line.strip():
                dataset, minimum, maximum = line.split()
                ranges.append((dataset, int(minimum), int(maximum)))

    return ranges


def check_ranges(geodatabase, ranges, logger, owner=None):

    badkount = 0

    for dataset, minimum, maximum in ranges:

        if owner:
            dataset = '{0}.{1}'.format(owner, dataset)

        try:
            kount = cscl_dataset.CSCLDataset(dataset).count(geodatabase)
        except Exception:
            logger.exception('Failed to count {0}'.format(dataset))
            kount = None

        if kount is None:
            badkount += 1
            logger.error('QA: no row count for {0}'.format(dataset))
        elif kount < minimum:
            badkount += 1
            logger.error(
                'QA: {0} has {1} rows, expected at least {2}'.format(
                    dataset, kount, minimum))
        elif kount > maximum:
            badkount += 1
            logger.error(
                'QA: {0} has {1} rows, expected at most {2}'.format(
                    dataset, kount, maximum))
        else:
            logger.info(
                'PASS: {0} has {1} rows (minimum {2} maximum {3})'.format(
                    dataset, kount, minimum, maximum))

    return badkount


def main():

    parser = argparse.ArgumentParser(description="QA CSCL dataset row counts")

    parser.add_argument("geodatabase", help="Path to the cscl geodatabase")
    parser.add_argument("logdir", help="Folder for logs")
    parser.add_argument("logname", help="Name of log")
    parser.add_argument("logmode", help="w(rite) or a(ppend)")
    parser.add_argument("--owner"
                       ,help="Schema owner for enterprise geodatabases (ex CSCL)"
                       ,default=None)
    parser.add_argument("--rowcountrange"
                       ,help="File of dataset minimum maximum row counts"
                       ,default=os.path.join(os.path.dirname(__file__)
                                            ,'resources'
                                            ,'rowcountrange'))

    args = parser.parse_args()

    setuplogger('qa_row_count'
               ,args.logname
               ,args.logdir
               ,args.logmode)
    logger = logging.getLogger('qa_row_count')

    logger.info('starting row count qa of {0}'.format(args.geodatabase))

    sys.exit(check_ranges(args.geodatabase
                         ,get_ranges(args.rowcountrange)
                         ,logger
                         ,args.owner))


if __name__ == '__main__':
    main()
