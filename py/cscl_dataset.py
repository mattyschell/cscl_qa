import os
import time
import sys
import arcpy


class CSCLDataset(object):

    def __init__(self
                ,datasetname):
         
        self.name = datasetname

        # not yet using this switch
        self.is_py2 = sys.version_info[0] == 2
        self.is_py3 = sys.version_info[0] == 3

        # featureclass, featuredataset, etc
        self.gdbtype = self._get_gdb_type()
        self.istable = self._get_tupletypes()

        # if this dataset is a part of of a deceitful featuredataset
        # this is the deceitful name (spoiler: its CSCL)
        self.featuredataset = self._get_featuredataset()

        if self.featuredataset is None:
            self.datasetpath = self.name
        else:
            self.datasetpath = os.path.join(self.featuredataset
                                           ,self.name)  

    def _get_cscl_list(self
                      ,whichlist):

        with open(os.path.join(os.path.dirname(__file__)
                              ,'resources'
                              ,whichlist)) as l:
            
            contents = [line.strip() for line in l]

        return contents  

    def _get_gdb_type(self):

        # what type of geodatabase item is this

        # EZ singular names. English can take the L
        typelist = ['featureclass'
                   ,'featuredataset'
                   ,'featuretable'
                   ,'relationshipclass'
                   ,'topology'
                   ,'archiveclass'
                   ,'domain'
                   ,'attributedrelationshipclass']
        
        for itemtype in typelist:
            if self.name in self._get_cscl_list('all' + itemtype):
                return itemtype
  
    def _get_featuredataset(self):

        # if self is in a feature dataset tell us the feature dataset name

        featuredatasets = self._get_cscl_list('allfeaturedataset')

        for featuredatasetname in featuredatasets:

            # just one (for now) deceitful featuredataset to loop over
        
            if self.name in self._get_cscl_list(featuredatasetname):
                return featuredatasetname
            
        return None

    def _get_tupletypes(self):

        if self.gdbtype in ('featureclass','featuretable','archiveclass','attributedrelationshipclass'): 
            return True
        else:
            return False

    def _get_field_type(self
                       ,gdb
                       ,field_name):

        fields = arcpy.ListFields(os.path.join(gdb, self.datasetpath)
                                 ,field_name)

        return fields[0].type # string, integer, double, etc

    def exists(self
              ,gdb):

        if arcpy.Exists(os.path.join(gdb, self.datasetpath)):
            return True
        else:
            return False   

    def count(self
             ,gdb):

        if self.istable:
            try:
                kount = int(arcpy.management.GetCount(os.path.join(gdb
                                                                  ,self.datasetpath))[0])
            except arcpy.ExecuteError:
                kount = 0
            return kount
        else:
            return None

    def attribute_exists(self
                        ,gdb
                        ,column
                        ,attribute
                        ,fuzzy=True):


        if not self.istable:
            return False

        try:
            field_type = self._get_field_type(gdb
                                             ,column)

            if field_type == 'String':
                targetattribute = attribute.lower()
            else:
                targetattribute = attribute

            def matches(value):
                if value is None:
                    return False
                if field_type == 'String':
                    if (fuzzy and targetattribute in value.lower()):
                        return True
                    elif targetattribute == value.lower():
                        return True
                    else:
                        return False
                else:
                    return value == targetattribute

            return any(
                matches(row[0])
                for row in arcpy.da.SearchCursor(os.path.join(gdb, self.datasetpath)
                                                ,[column])
            )
        except arcpy.ExecuteError:
            return False
   
