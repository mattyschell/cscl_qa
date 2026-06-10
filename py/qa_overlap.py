import argparse
import logging
import sys

from logging_utils import setuplogger
from polygon_qa import PolygonQa


def qa_overlap(feature_class
              ,geodatabase
			  ,tolerance
			  ,logger):
	overlap_result = PolygonQa(feature_class
	                          ,geodatabase).check_overlap(tolerance)

	logger.info("feature_class={0}".format(overlap_result.feature_class_path))
	logger.info("total_area={0}".format(overlap_result.total_area))
	logger.info("aggregated_area={0}".format(overlap_result.aggregated_area))
	logger.info("overlap_area={0}".format(overlap_result.overlap_area))
	logger.info("tolerance={0}".format(tolerance))

	if overlap_result.has_overlap:
		logger.warning(
			"QA: overlap area {0} exceeds tolerance {1} on {2}".format(
				overlap_result.overlap_area,
				tolerance,
				overlap_result.feature_class_path,
			)
		)
	else:
		logger.info(
			"PASS: overlap area {0} within tolerance {1} on {2}".format(
				overlap_result.overlap_area,
				tolerance,
				overlap_result.feature_class_path,
			)
		)

	return overlap_result.has_overlap


def main():
	parser = argparse.ArgumentParser(
		description="QA a polygon feature class for row-level spatial overlaps"
	)
	parser.add_argument("featureclass", help="Input feature class name or path")
	parser.add_argument("geodatabase", help="Input geodatabase path")
	parser.add_argument("logdir", help="Folder for logs")
	parser.add_argument("logname", help="Name of log")
	parser.add_argument("logmode", help="w(rite) or a(ppend)")
	parser.add_argument(
		"tolerance",
		type=float,
		help="Allowed overlap area tolerance (same units as feature class area)",
	)
	args = parser.parse_args()

	setuplogger('qa_overlap'
			   ,args.logname
			   ,args.logdir
			   ,args.logmode)
	logger = logging.getLogger('qa_overlap')

	logger.info('starting qa overlap of {0}'.format(args.featureclass))

	has_overlap = qa_overlap(args.featureclass
					,args.geodatabase
					,args.tolerance
					,logger)
	sys.exit(1 if has_overlap else 0)


if __name__ == "__main__":
	main()
