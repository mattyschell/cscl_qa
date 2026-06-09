import argparse
import os
import sys
import uuid

import arcpy


def resolve_feature_class(feature_class, geodatabase):
	if arcpy.Exists(feature_class):
		return feature_class

	candidate = os.path.join(geodatabase, feature_class)
	if arcpy.Exists(candidate):
		return candidate

	raise ValueError(
		"Could not find feature class '{0}' in geodatabase '{1}'".format(
			feature_class,
			geodatabase,
		)
	)


def get_total_area(feature_class_path):
	total_area = 0.0
	with arcpy.da.SearchCursor(feature_class_path, ["SHAPE@AREA"]) as cursor:
		for row in cursor:
			if row[0] is not None:
				total_area += row[0]
	return total_area


def get_aggregated_area(feature_class_path):
	dissolved_fc = os.path.join("in_memory", "qa_overlap_{0}".format(uuid.uuid4().hex))
	try:
		if hasattr(arcpy.analysis, "PairwiseDissolve"):
			arcpy.analysis.PairwiseDissolve(feature_class_path, dissolved_fc)
		else:
			arcpy.management.Dissolve(feature_class_path, dissolved_fc)
		dissolved_area = 0.0
		with arcpy.da.SearchCursor(dissolved_fc, ["SHAPE@AREA"]) as cursor:
			for row in cursor:
				if row[0] is not None:
					dissolved_area += row[0]
		return dissolved_area
	finally:
		if arcpy.Exists(dissolved_fc):
			arcpy.management.Delete(dissolved_fc)


def qa_overlap(feature_class, geodatabase, tolerance):
	feature_class_path = resolve_feature_class(feature_class, geodatabase)

	shape_type = arcpy.Describe(feature_class_path).shapeType
	if shape_type != "Polygon":
		raise ValueError(
			"qa_overlap requires a Polygon feature class. Found shape type '{0}'".format(
				shape_type
			)
		)

	total_area = get_total_area(feature_class_path)
	aggregated_area = get_aggregated_area(feature_class_path)
	overlap_area = total_area - aggregated_area

	print("feature_class={0}".format(feature_class_path))
	print("total_area={0}".format(total_area))
	print("aggregated_area={0}".format(aggregated_area))
	print("overlap_area={0}".format(overlap_area))
	print("tolerance={0}".format(tolerance))

	return overlap_area > tolerance


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
