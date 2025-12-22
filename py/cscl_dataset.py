import os
import time
import sys
import arcpy


class CSCLDataset(object):

    def __init__(self
                ,dataset):
         
        self.dataset = dataset

        # usually CSCL.xyz
        # but we allow xyz if the caller uses a file geodatabase or the caller is CSCL
        self.owner, self.name = self._filterschema()

        # TBD on using this property.  Some commits yes, some no.
        if sys.version_info[0] == 2:
            self.arcpyversion = 2
        elif sys.version_info[0] == 3:
            self.arcpyversion = 3

        # featureclass, featuredataset, etc
        self.gdbtype     = self._get_gdb_type()
        self.istable     = self._get_tupletypes()
        self.businesskey = self._get_businesskey()

        # if this dataset is a part of of a deceitful featuredataset
        # this is the deceitful name (spoiler: its CSCL)
        self.featuredataset = self._get_featuredataset()
  
    def _get_dataset_path(self
                         ,owner=None):

        fc = "%s.%s" % (owner, self.name) if owner else self.name

        if self.featuredataset is None:
            return fc
        else:    
            fd = "%s.%s" % (owner, self.featuredataset) if owner else self.featuredataset
            return os.path.join(fd,fc)

    def _get_cscl_list(self
                      ,whichlist):

        with open(os.path.join(os.path.dirname(__file__)
                              ,'resources'
                              ,whichlist)) as l:
            
            # by convention upper case when matching to the list 
            contents = [line.strip().upper() for line in l]

        return contents  

    def _filterschema(self):

        # inputs CSCL.BOROUGH jdoe.Foo Borough Foo

        if '.' in self.dataset:
            return (self.dataset.partition('.')[0]
                   ,self.dataset.partition('.')[2])
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
            if self.name.upper() in self._get_cscl_list('all' + itemtype):
                return itemtype
        
        if itemtype is None:
            raise ValueError('{0} does not appear in our lists of resources'.format(self.name))

    def _get_businesskey(self):

        #for datasetkey in self._get_cscl_list('allbusinesskey'):

        lookup = {k:v for k, v in (item.split() for 
            item in self._get_cscl_list('allbusinesskey'))}

        return lookup.get(self.name.upper())
  
    def _get_featuredataset(self):

        # if self is in a feature dataset tell us the feature dataset name

        featuredatasets = self._get_cscl_list('allfeaturedataset')

        for featuredatasetname in featuredatasets:

            # just one (for now) deceitful featuredataset to loop over
        
            if self.name.upper() in self._get_cscl_list(featuredatasetname):
                return featuredatasetname
            
        return None

    def _get_tupletypes(self):

        if self.gdbtype in ('featureclass'
                           ,'featuretable'
                           ,'archiveclass'
                           ,'attributedrelationshipclass'): 
            return True
        else:
            return False

    def _get_field_type(self
                       ,gdb
                       ,field_name):

        fields = arcpy.ListFields(os.path.join(gdb, self._get_path_in_gdb(gdb))
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

    def _get_path_in_gdb(self
                        ,gdb):

        # we typically initialize using an enterprise geodatabase
        # but children may be in a file geodatabase without schema owners

        # workspaceFactoryProgID is only available in pro python
        desc = arcpy.Describe(gdb)

        if (desc.workspaceType.endswith('LocalDatabase') 
        or  desc.workspaceFactoryProgID.endswith('FileGDBWorkspaceFactory')):
            # get path without owner
            return self._get_dataset_path()
        else:
            return self._get_dataset_path(self.owner)          

    def exists(self
              ,gdb):

        if (self._gdb_exists(gdb) and \
            arcpy.Exists(os.path.join(gdb, self._get_path_in_gdb(gdb)))):
            return True
        else:
            return False   

    def count(self
             ,gdb):

        if (self._gdb_exists(gdb) and \
            self.istable):
            try:
                kount = int(arcpy.management.GetCount(os.path.join(gdb
                                                                  ,self._get_path_in_gdb(gdb)))[0])
                return kount
            except arcpy.ExecuteError:
                # this typically means arcpy3 hitting a legacy dataset with class extensions
                raise ValueError('Couldnt get a count for ' \
                                '{0} using arcpy {1}. Details: {2}'.format(os.path.join(gdb,self._get_path_in_gdb(gdb))
                                                                          ,self.arcpyversion
                                                                          ,arcpy.GetMessages(2)))
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

            if attribute == '' or attribute == None:
                targetattribute = None
            elif field_type == 'String' and attribute is not None:
                targetattribute = attribute.lower()
            else:
                # if storage string, the attribute here should be 
                # forced to match the storage datatype
                targetattribute = self._safe_to_number(attribute)

            def matches(value):
                if (value is None or value == "") and targetattribute is not None:
                    # esri: empty string and None have different semantics
                    # mschell: "whats a semantic?" 
                    return False
                elif (value is None or value == "") and targetattribute is None:
                    return True
                elif value is not None and targetattribute is None:
                    return False
                elif field_type == 'String':
                    if (fuzzy and targetattribute in value.lower()):
                        return True
                    elif targetattribute == value.lower():
                        return True
                    else:
                        return False
                else:
                    # numeric or... more
                    return value == targetattribute

            return any(
                matches(row[0])
                for row in arcpy.da.SearchCursor(os.path.join(gdb, self._get_path_in_gdb(gdb))
                                                ,[column])
            )
        except arcpy.ExecuteError:
            return False
   
