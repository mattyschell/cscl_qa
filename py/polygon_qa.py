import os
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


class OverlapCheckResult(object):

	def __init__(self,
				 feature_class_path,
				 total_area,
				 aggregated_area,
				 overlap_area,
				 tolerance):
		self.feature_class_path = feature_class_path
		self.total_area = total_area
		self.aggregated_area = aggregated_area
		self.overlap_area = overlap_area
		self.tolerance = tolerance

	@property
	def has_overlap(self):
		return self.overlap_area > self.tolerance

	def print_summary(self):
		print("feature_class={0}".format(self.feature_class_path))
		print("total_area={0}".format(self.total_area))
		print("aggregated_area={0}".format(self.aggregated_area))
		print("overlap_area={0}".format(self.overlap_area))
		print("tolerance={0}".format(self.tolerance))


class PolygonQa(object):

	def __init__(self,
				 feature_class,
				 geodatabase):
		self.feature_class = feature_class
		self.geodatabase = geodatabase
		self.feature_class_path = resolve_feature_class(feature_class
												   ,geodatabase)

	def _get_shape_type(self):
		return arcpy.Describe(self.feature_class_path).shapeType

	def _require_polygon(self, check_name):
		shape_type = self._get_shape_type()
		if shape_type != "Polygon":
			raise ValueError(
				"{0} requires a Polygon feature class. Found shape type '{1}'".format(
					check_name,
					shape_type
				)
			)

	def get_total_area(self):
		total_area = 0.0
		with arcpy.da.SearchCursor(self.feature_class_path, ["SHAPE@AREA"]) as cursor:
			for row in cursor:
				if row[0] is not None:
					total_area += row[0]
		return total_area

	def get_aggregated_area(self):
		dissolved_fc = os.path.join("in_memory", "qa_overlap_{0}".format(uuid.uuid4().hex))
		try:
			if hasattr(arcpy.analysis, "PairwiseDissolve"):
				arcpy.analysis.PairwiseDissolve(self.feature_class_path, dissolved_fc)
			else:
				arcpy.management.Dissolve(self.feature_class_path, dissolved_fc)
			dissolved_area = 0.0
			with arcpy.da.SearchCursor(dissolved_fc, ["SHAPE@AREA"]) as cursor:
				for row in cursor:
					if row[0] is not None:
						dissolved_area += row[0]
			return dissolved_area
		finally:
			if arcpy.Exists(dissolved_fc):
				arcpy.management.Delete(dissolved_fc)

	def check_overlap(self
					 ,tolerance
					 ,check_name='qa_overlap'):
		self._require_polygon(check_name)

		total_area = self.get_total_area()
		aggregated_area = self.get_aggregated_area()
		overlap_area = total_area - aggregated_area

		return OverlapCheckResult(self.feature_class_path
							 ,total_area
							 ,aggregated_area
							 ,overlap_area
							 ,tolerance)