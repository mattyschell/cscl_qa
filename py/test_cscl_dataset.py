import unittest
import os

import cscl_dataset

class CSCLDatasetTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__)
                                                     ,".."))

        self.borough       = cscl_dataset.CSCLDataset('Borough')

        self.sourcegdb     = os.path.join(self.repo_root
                                         ,'testdata'
                                         ,'source.gdb')
        self.goodtargetgdb = os.path.join(self.repo_root
                                         ,'testdata'
                                         ,'goodtarget.gdb')
        self.badtargetgdb  = os.path.join(self.repo_root
                                         ,'testdata'
                                         ,'badtarget.gdb')

    def test_afeatureclass(self):
        
        self.assertEqual(self.borough.name
                        ,'Borough')

        self.assertIsNone(self.borough.featuredataset)

        self.assertEqual(self.borough.gdbtype
                        ,'featureclass')

        self.assertTrue(self.borough.istable)

    def test_bfeatureclassexists(self):

        self.assertTrue(self.borough.exists(self.sourcegdb))
        self.assertTrue(self.borough.exists(self.goodtargetgdb))
        self.assertTrue(self.borough.exists(self.badtargetgdb))

    def test_cqacount(self):

        self.assertEqual(self.borough.count(self.sourcegdb)
                        ,self.borough.count(self.goodtargetgdb))

        self.assertNotEqual(self.borough.count(self.sourcegdb)
                           ,self.borough.count(self.badtargetgdb))

    def test_dpyversion(self):

        self.assertEqual({self.borough.is_py2, self.borough.is_py3}
                        ,{True, False})

    def test_eattributeexists(self):

        self.assertTrue(self.borough.attribute_exists(self.sourcegdb
                                                     ,'BoroName'
                                                     ,'Manhattan'))

        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                      ,'BoroName'
                                                      ,'Philadelphia'))

        self.assertTrue(self.borough.attribute_exists(self.sourcegdb
                                                     ,'BoroCode'
                                                     ,1))

        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                      ,'BoroCode'
                                                      ,6))

        # fuzzy match
        self.assertTrue(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroName'
                                                     ,'JUNK'))
        
        self.assertTrue(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroName'
                                                     ,'Junk'))

        self.assertTrue(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroName'
                                                     ,'junk'))

        # exact match (still case insensitive)
        self.assertFalse(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroName'
                                                     ,'JUNK'
                                                     ,False))

        self.assertTrue(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroName'
                                                     ,'Staten junk Island'
                                                     ,False))                                                     

if __name__ == '__main__':
    unittest.main()