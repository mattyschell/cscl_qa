import os
import time
import sys
import arcpy


class CSCLDataset(object):

    def __init__(self
                ,dataset):
         
        self.dataset = dataset
        self.owner, self.name = self._filterschema()

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
            self.datasetpath = self.dataset
        else:
            if self.owner is None:
                self.datasetpath = os.path.join(self.featuredataset
                                               ,self.dataset)  
            else:
                self.datasetpath = os.path.join('{0}.{1}'.format(self.owner
                                                                ,self.featuredataset)
                                               ,self.dataset)  

    def _get_cscl_list(self
                      ,whichlist):

        with open(os.path.join(os.path.dirname(__file__)
                              ,'resources'
                              ,whichlist)) as l:
            
            contents = [line.strip() for line in l]

        return contents  

    def _filterschema(self):

        # input like CSCL.BOROUGH jdoe.Foo or just Borough

        if '.' in self.dataset:
            return self.dataset.partition('.')[0], self.dataset.partition('.')[2]
        else:
            return None, self.dataset

    def _get_gdb_type(self):

        # what type of geodatabase item is this
        # EZ singular names. English can take the L
        typelist = ['featureclass'
                   ,'featuredataset'
                   ,'featuretable'
                   ,'attributedrelationshipclass' # overlaps next must go first
                   ,'relationshipclass'
                   ,'topology'
                   ,'archiveclass'
                   ,'domain']
        
        for itemtype in typelist:
            if self.name in self._get_cscl_list('all' + itemtype):
                return itemtype
        
        if itemtype is None:
            raise ValueError('{0} does not appear in our lists of resources'.format(self.name))
  
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
    
    def _gdb_exists(self
                   ,gdb):

        # simple helper. 
        # Paths on VMs and network connectivity can be messy

        if not arcpy.Exists(gdb):
            raise ValueError('Geodatabase path {0} is not valid'.format(gdb))

        if arcpy.Describe(gdb).dataType not in ('Workspace'
                                               ,'SDEWorkspace'):
            raise ValueError('{0} is not a valid geodatabase'.format(gdb))
        
        return True
    
    def _safe_to_number(self
                       ,value):
        try:
            num = float(value)
            return int(num) if num.is_integer() else num
        except (ValueError, TypeError):
            return value

    def exists(self
              ,gdb):

        if (self._gdb_exists(gdb) and \
            arcpy.Exists(os.path.join(gdb, self.datasetpath))):
            return True
        else:
            return False   

    def count(self
             ,gdb):

        if (self._gdb_exists(gdb) and \
            self.istable):
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

        if (self._gdb_exists(gdb) and not \
            self.istable):
            return False

        try:
            field_type = self._get_field_type(gdb
                                             ,column)

            if field_type == 'String':
                targetattribute = attribute.lower()
            else:
                # string input attribute should be made to match the storage datatype
                targetattribute = self._safe_to_number(attribute)

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
                    #print('comparing {0} to {1}'.format(value, targetattribute))
                    return value == targetattribute

            return any(
                matches(row[0])
                for row in arcpy.da.SearchCursor(os.path.join(gdb, self.datasetpath)
                                                ,[column])
            )
        except arcpy.ExecuteError:
            return False
   
