import logging
import os
import unittest

import cscl_dataset
import qa_row_count


class RowCountQaTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..'))
        cls.geodatabase = os.path.join(cls.repo_root
                                      ,'testdata'
                                      ,'source.gdb')
        cls.borough = cscl_dataset.CSCLDataset('Borough')
        cls.borough_count = cls.borough.count(cls.geodatabase)
        cls.logger = logging.getLogger('test_row_count')
        cls.logger.setLevel(logging.CRITICAL)

    def test_count_within_inclusive_range_passes(self):
        result = qa_row_count.check_ranges(
            self.geodatabase,
            [('Borough', self.borough_count, self.borough_count)],
            self.logger)

        self.assertEqual(result, 0)

    def test_count_below_minimum_fails(self):
        result = qa_row_count.check_ranges(
            self.geodatabase,
            [('Borough', self.borough_count + 1, self.borough_count + 1)],
            self.logger)

        self.assertEqual(result, 1)

    def test_count_above_maximum_fails(self):
        result = qa_row_count.check_ranges(
            self.geodatabase,
            [('Borough', self.borough_count - 1, self.borough_count - 1)],
            self.logger)

        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()