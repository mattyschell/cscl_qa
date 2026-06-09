import argparse
import sys

from polygon_qa import PolygonQa


def qa_overlap(feature_class, geodatabase, tolerance):
	overlap_result = PolygonQa(feature_class, geodatabase).check_overlap(tolerance)
	overlap_result.print_summary()
	return overlap_result.has_overlap


def main():
	parser = argparse.ArgumentParser(
		description="QA a polygon feature class for row-level spatial overlaps"
	)
	parser.add_argument("featureclass", help="Input feature class name or path")
	parser.add_argument("geodatabase", help="Input geodatabase path")
	parser.add_argument(
		"tolerance",
		type=float,
		help="Allowed overlap area tolerance (same units as feature class area)",
	)
	args = parser.parse_args()

	has_overlap = qa_overlap(args.featureclass, args.geodatabase, args.tolerance)
	sys.exit(1 if has_overlap else 0)


if __name__ == "__main__":
	main()
