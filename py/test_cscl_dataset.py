import unittest
import os

import cscl_dataset

class CSCLDatasetTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.repo_root     = os.path.abspath(os.path.join(os.path.dirname(__file__)
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

        self.nonexistentgdb = os.path.join(self.repo_root
                                          ,'testdata'
                                          ,'maltagoya.gdb')
        
        # no test data for these but we test the resource wrangling
        # schema is a firm requirement because when possible 
        # we will run QA from a read-only user
        self.boroughwithschema              = cscl_dataset.CSCLDataset('MALTAGOYA.Borough')
        self.rail_schema_featuredataset     = cscl_dataset.CSCLDataset('MALTAGOYA.Rail')
        self.subwaystationshavefeaturenames = cscl_dataset.CSCLDataset('MALTAGOYA.SubwayStationsHaveFeatureNames')

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

    def test_ffilterschema(self): 

        self.assertEqual(self.boroughwithschema.name
                        ,'Borough')

        self.assertEqual(self.boroughwithschema.owner
                        ,'MALTAGOYA')

        self.assertIsNone(self.boroughwithschema.featuredataset)

        self.assertEqual(self.boroughwithschema.gdbtype
                        ,'featureclass')

        self.assertTrue(self.boroughwithschema.istable)

        self.assertEqual(self.boroughwithschema.datasetpath
                       ,'MALTAGOYA.Borough')     

    def test_gschemaandfeaturedataset(self):
        
        self.assertEqual(self.rail_schema_featuredataset.name
                        ,'Rail')

        self.assertEqual(self.rail_schema_featuredataset.owner
                        ,'MALTAGOYA')

        self.assertEqual(self.rail_schema_featuredataset.featuredataset
                        ,'CSCL')

        self.assertEqual(self.rail_schema_featuredataset.gdbtype
                        ,'featureclass')

        self.assertTrue(self.rail_schema_featuredataset.istable)

        # this may not be correct but for now it is what it is
        self.assertEqual(self.rail_schema_featuredataset.datasetpath
                       ,'MALTAGOYA.CSCL\MALTAGOYA.Rail')     

    def test_hattributedrelationshipclass(self):
        
        self.assertEqual(self.subwaystationshavefeaturenames.name
                        ,'SubwayStationsHaveFeatureNames')

        self.assertEqual(self.subwaystationshavefeaturenames.owner
                        ,'MALTAGOYA')

        self.assertIsNone(self.subwaystationshavefeaturenames.featuredataset)

        self.assertEqual(self.subwaystationshavefeaturenames.gdbtype
                        ,'attributedrelationshipclass')

        self.assertTrue(self.subwaystationshavefeaturenames.istable)

        self.assertEqual(self.subwaystationshavefeaturenames.datasetpath
                       ,'MALTAGOYA.SubwayStationsHaveFeatureNames') 

    def test_ibadgdbraises(self): 
        
        with self.assertRaises(ValueError):
            self.borough.exists(self.nonexistentgdb)

        with self.assertRaises(ValueError):
            self.borough.count(self.nonexistentgdb)
            
        with self.assertRaises(ValueError):
            self.borough.attribute_exists(self.nonexistentgdb
                                         ,'BoroName'
                                         ,'Manhattan')
                                                          

if __name__ == '__main__':
    unittest.main()