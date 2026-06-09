import os
import sys
import unittest


class Namespace(object):

	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			setattr(self, key, value)


class FakeCursor(object):

	def __init__(self, rows):
		self._rows = rows

	def __enter__(self):
		return iter(self._rows)

	def __exit__(self, exc_type, exc_value, traceback):
		return False


class FakeArcpy(object):

	def __init__(self,
				 existing_paths,
				 describe_map,
				 area_map,
				 pairwise_available=True):
		self.existing_paths = set(existing_paths)
		self.describe_map = describe_map
		self.area_map = area_map
		self.deleted_paths = []
		self.pairwise_calls = []
		self.dissolve_calls = []
		self.da = Namespace(SearchCursor=self._search_cursor)
		self.management = Namespace(
			Dissolve=self._dissolve,
			Delete=self._delete,
		)
		self.analysis = Namespace()
		if pairwise_available:
			self.analysis.PairwiseDissolve = self._pairwise_dissolve

	def Exists(self, path):
		return path in self.existing_paths

	def Describe(self, path):
		return Namespace(shapeType=self.describe_map[path])

	def _search_cursor(self, path, fields):
		return FakeCursor(self.area_map[path])

	def _pairwise_dissolve(self, source, target):
		self.pairwise_calls.append((source, target))
		self.existing_paths.add(target)

	def _dissolve(self, source, target):
		self.dissolve_calls.append((source, target))
		self.existing_paths.add(target)

	def _delete(self, path):
		self.deleted_paths.append(path)
		self.existing_paths.discard(path)


class PolygonQaTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.py_dir = os.path.dirname(__file__)
		if cls.py_dir not in sys.path:
			sys.path.insert(0, cls.py_dir)

	def setUp(self):
		self.original_polygon_qa = sys.modules.get('polygon_qa')
		self.original_arcpy = sys.modules.get('arcpy')

	def tearDown(self):
		sys.modules.pop('polygon_qa', None)
		sys.modules.pop('arcpy', None)
		if self.original_polygon_qa is not None:
			sys.modules['polygon_qa'] = self.original_polygon_qa
		if self.original_arcpy is not None:
			sys.modules['arcpy'] = self.original_arcpy

	def _import_module(self, fake_arcpy):
		sys.modules['arcpy'] = fake_arcpy
		return __import__('polygon_qa')

	def test_resolve_feature_class_prefers_explicit_path(self):
		fake_arcpy = FakeArcpy(
			existing_paths=['standalone_fc'],
			describe_map={'standalone_fc': 'Polygon'},
			area_map={'standalone_fc': [(1.0,)]},
		)

		polygon_qa = self._import_module(fake_arcpy)

		self.assertEqual(
			polygon_qa.resolve_feature_class('standalone_fc', 'workspace.gdb'),
			'standalone_fc'
		)

	def test_check_overlap_returns_structured_result(self):
		feature_class_path = os.path.join('workspace.gdb', 'Borough')
		dissolved_path = os.path.join('in_memory', 'qa_overlap_result_fc')
		fake_arcpy = FakeArcpy(
			existing_paths=[feature_class_path, dissolved_path],
			describe_map={feature_class_path: 'Polygon'},
			area_map={
				feature_class_path: [(5.0,), (7.0,)],
				dissolved_path: [(10.0,)],
			},
		)

		polygon_qa = self._import_module(fake_arcpy)
		polygon_qa.uuid.uuid4 = lambda: Namespace(hex='result_fc')

		result = polygon_qa.PolygonQa('Borough', 'workspace.gdb').check_overlap(1.5)

		self.assertEqual(result.feature_class_path, feature_class_path)
		self.assertAlmostEqual(result.total_area, 12.0, delta=0.001)
		self.assertAlmostEqual(result.aggregated_area, 10.0, delta=0.001)
		self.assertAlmostEqual(result.overlap_area, 2.0, delta=0.001)
		self.assertEqual(result.tolerance, 1.5)
		self.assertTrue(result.has_overlap)
		self.assertEqual(len(fake_arcpy.pairwise_calls), 1)
		self.assertEqual(fake_arcpy.deleted_paths, [dissolved_path])

	def test_check_overlap_requires_polygon_geometry(self):
		feature_class_path = os.path.join('workspace.gdb', 'Centerline')
		fake_arcpy = FakeArcpy(
			existing_paths=[feature_class_path],
			describe_map={feature_class_path: 'Polyline'},
			area_map={feature_class_path: []},
		)

		polygon_qa = self._import_module(fake_arcpy)

		with self.assertRaises(ValueError) as context:
			polygon_qa.PolygonQa('Centerline', 'workspace.gdb').check_overlap(0.0)

		self.assertIn("qa_overlap requires a Polygon feature class"
		             ,str(context.exception))

	def test_check_overlap_falls_back_to_management_dissolve(self):
		feature_class_path = os.path.join('workspace.gdb', 'Borough')
		dissolved_path = os.path.join('in_memory', 'qa_overlap_result_fc')
		fake_arcpy = FakeArcpy(
			existing_paths=[feature_class_path, dissolved_path],
			describe_map={feature_class_path: 'Polygon'},
			area_map={
				feature_class_path: [(4.0,), (6.0,)],
				dissolved_path: [(10.0,)],
			},
			pairwise_available=False,
		)

		polygon_qa = self._import_module(fake_arcpy)
		polygon_qa.uuid.uuid4 = lambda: Namespace(hex='result_fc')

		result = polygon_qa.PolygonQa('Borough'
		                             ,'workspace.gdb').check_overlap(0.0)

		self.assertFalse(hasattr(fake_arcpy.analysis, 'PairwiseDissolve'))
		self.assertEqual(len(fake_arcpy.dissolve_calls), 1)
		self.assertFalse(result.has_overlap)


class PolygonQaIntegrationTestCase(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.py_dir = os.path.dirname(__file__)
		if cls.py_dir not in sys.path:
			sys.path.insert(0, cls.py_dir)

		cls.repo_root = os.path.abspath(os.path.join(cls.py_dir, '..'))
		cls.overlap_gdb = os.path.join(cls.repo_root
		                              ,'testdata'
									  ,'overlap.gdb')

		import arcpy
		cls.arcpy = arcpy

	def setUp(self):
		self.original_polygon_qa = sys.modules.get('polygon_qa')
		self.original_arcpy = sys.modules.get('arcpy')
		sys.modules.pop('polygon_qa', None)
		sys.modules['arcpy'] = self.arcpy

	def tearDown(self):
		sys.modules.pop('polygon_qa', None)
		if self.original_polygon_qa is not None:
			sys.modules['polygon_qa'] = self.original_polygon_qa
		if self.original_arcpy is not None:
			sys.modules['arcpy'] = self.original_arcpy
		else:
			sys.modules.pop('arcpy', None)

	def _import_module(self):
		return __import__('polygon_qa')

	def test_overlap_fixture_exists(self):
		self.assertTrue(self.arcpy.Exists(self.overlap_gdb))

	def test_goodborough_has_no_overlap(self):
		polygon_qa = self._import_module()
		goodborough_tolerance = 0.1

		result = polygon_qa.PolygonQa('goodborough'
                                     ,self.overlap_gdb).check_overlap(
                                        goodborough_tolerance)

		self.assertEqual(
			result.feature_class_path,
			os.path.join(self.overlap_gdb, 'goodborough')
		)
		self.assertLessEqual(result.overlap_area, goodborough_tolerance)
		self.assertFalse(result.has_overlap)

	def test_badborough_has_overlap(self):
		polygon_qa = self._import_module()

		result = polygon_qa.PolygonQa('badborough'
                                     ,self.overlap_gdb).check_overlap(0.0)

		self.assertEqual(
			result.feature_class_path,
			os.path.join(self.overlap_gdb, 'badborough')
		)
		self.assertGreater(result.overlap_area, 0.0)
		self.assertTrue(result.has_overlap)


if __name__ == '__main__':
	unittest.main()