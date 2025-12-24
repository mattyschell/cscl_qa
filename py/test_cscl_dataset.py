import unittest
import os

import cscl_dataset

class CSCLDatasetTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.repo_root     = os.path.abspath(
                                os.path.join(os.path.dirname(__file__)
                                            ,".."))

        self.borough       = cscl_dataset.CSCLDataset('Borough')
        self.upperborough  = cscl_dataset.CSCLDataset('BOROUGH')

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
        
        # these exist in the test data (sans schema)
        # schema management is a firm requirement because when 
        # possible we will run QA from a read-only user
        self.boroughwithschema = (
            cscl_dataset.CSCLDataset('MALTAGOYA.Borough')
        )
        self.rail_schema_featuredataset = (    
            cscl_dataset.CSCLDataset('MALTAGOYA.Rail')
        )
        # no test data for these but we test the resource wrangling
        self.subwaystationshavefeaturenames = (
            cscl_dataset.CSCLDataset(
                'MALTAGOYA.SubwayStationsHaveFeatureNames'
                )
        )
        self.borougharchive = (
            cscl_dataset.CSCLDataset('MALTAGOYA.BOROUGH_H')
        )

    def test_afeatureclass(self):
        
        self.assertEqual(self.borough.name
                        ,'Borough')

        self.assertIsNone(self.borough.featuredataset)

        self.assertEqual(self.borough.gdbtype
                        ,'featureclass')

        self.assertTrue(self.borough.istable)

        self.assertEqual(self.borough.businesskey
                        ,'BOROCODE')

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

        self.assertTrue(self.borough.arcpyversion in (2,3)) 

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
        # the actual value in the test data is "Staten junk Island"
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

        self.assertTrue(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroCode'
                                                     ,1))

        # argparse inputs from python scripts will 
        # treat the attribute as a string
        # input attributes should be made to match the storage datatype
        # borocode is numeric '1' should be converted to 1 and match
        self.assertTrue(self.borough.attribute_exists(self.sourcegdb
                                                     ,'BoroCode'
                                                     ,'1'))

        self.assertTrue(self.borough.attribute_exists(self.sourcegdb
                                                     ,'BoroCode'
                                                     ,'1.00'))

        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                      ,'BoroCode'
                                                      ,'6'))
                                                      
        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                      ,'BoroCode'
                                                      ,'1.01'))

        # this precision is not necessarily displayed in catalog
        # here we are at the limits of floating point numbers
        #     catalog shows 1186614016.2245
        # Staten Island shows 1623758505.75111 and that is the match
        # exact match
        self.assertTrue(self.borough.attribute_exists(self.sourcegdb
                                                     ,'Shape_Area'
                                                     ,1186614016.2245002))
        
        self.assertTrue(self.borough.attribute_exists(self.sourcegdb
                                                     ,'Shape_Area'
                                                     ,'1186614016.2245002'))

        # here we have added one more digit than is supported by floats
        # this attribute exists. the 8th place 1 is nonexistent 
        # float(1186614016.22450021) returns 1186614016.2245002
        self.assertTrue(self.borough.attribute_exists(self.sourcegdb
                                                     ,'Shape_Area'
                                                     ,1186614016.22450021))
        
        self.assertTrue(self.borough.attribute_exists(self.sourcegdb
                                                     ,'Shape_Area'
                                                     ,'1186614016.22450021'))

        # here we are back in the realm of supported floats
        # this should not match
        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                     ,'Shape_Area'
                                                     ,1186614016.224500))
        
        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                     ,'Shape_Area'
                                                     ,'1186614016.224500'))

        # find null. best practice is to use None
        self.assertTrue(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroName'
                                                     ,None))
        # find null. we will coerce empty string to None
        self.assertTrue(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroName'
                                                     ,''))

        # confirm we can find nulls in numeric columns
        self.assertTrue(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroCode'
                                                     ,None))
        self.assertTrue(self.borough.attribute_exists(self.badtargetgdb
                                                     ,'BoroCode'
                                                     ,''))

        # check good gdb for Null in string column should return False
        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                      ,'BoroName'
                                                      ,None))                                         
        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                      ,'BoroName'
                                                      ,''))

        # check good gdb for Null in numeric column should return False
        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                      ,'BoroCode'
                                                      ,None))                                         
        self.assertFalse(self.borough.attribute_exists(self.sourcegdb
                                                      ,'BoroCode'
                                                      ,''))
        
    def test_ffilterschema(self): 

        self.assertEqual(self.boroughwithschema.name
                        ,'Borough')

        self.assertEqual(self.boroughwithschema.owner
                        ,'MALTAGOYA')

        self.assertIsNone(self.boroughwithschema.featuredataset)

        self.assertEqual(self.boroughwithschema.gdbtype
                        ,'featureclass')

        self.assertTrue(self.boroughwithschema.istable)   

        # this should drop the schema when checking a file geodatabase
        self.assertTrue(self.boroughwithschema.exists(self.sourcegdb)) 

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

        self.assertTrue(self.rail_schema_featuredataset.exists(self.sourcegdb))

        self.assertEqual(self.rail_schema_featuredataset.count(self.sourcegdb)
                        ,0)  

        self.assertFalse(
            self.rail_schema_featuredataset.attribute_exists(
                self.sourcegdb
               ,'SegmentId'
               ,123456789)  
            )

    def test_hattributedrelationshipclass(self):
        
        self.assertEqual(self.subwaystationshavefeaturenames.name
                        ,'SubwayStationsHaveFeatureNames')

        self.assertEqual(self.subwaystationshavefeaturenames.owner
                        ,'MALTAGOYA')

        self.assertIsNone(self.subwaystationshavefeaturenames.featuredataset)

        self.assertEqual(self.subwaystationshavefeaturenames.gdbtype
                        ,'attributedrelationshipclass')

        self.assertTrue(self.subwaystationshavefeaturenames.istable)

        self.assertEqual(self.subwaystationshavefeaturenames.businesskey
                        ,'GLOBALID')

    def test_ibadgdbraises(self): 
        
        # py 2 vs 3 differences
        with self.assertRaises((ValueError,IOError,OSError)):
            self.borough.exists(self.nonexistentgdb)

        with self.assertRaises(ValueError):
            self.borough.count(self.nonexistentgdb)
            
        with self.assertRaises(ValueError):
            self.borough.attribute_exists(self.nonexistentgdb
                                         ,'BoroName'
                                         ,'Manhattan')

    def test_jupperfeatureclass(self):

        self.assertEqual(self.upperborough.name
                        ,'BOROUGH')

        self.assertIsNone(self.upperborough.featuredataset)

        self.assertEqual(self.upperborough.gdbtype
                        ,'featureclass')

        self.assertTrue(self.upperborough.istable)

    def test_kbusinesskey(self):

        self.assertEqual(self.borough.businesskey
                        ,'BOROCODE')

        self.assertEqual(self.boroughwithschema.businesskey
                        ,'BOROCODE')

        # we have not fully populated resources/allbusinesskey
        # also some item types will never have business keys
        self.assertIsNone(self.borougharchive.businesskey)


if __name__ == '__main__':
    unittest.main()