# CSCL_QA

Miscellaneous quality assurance checks of NYC's top banana geodatabase.  Friends, this is our banana quality assurance, our rules, the trick is never to be afraid.

### QA a CSCL dataset

Report suspect values.  Intended for use with a live CSCL version.

```text
usage: qa_one_dataset.py [-h] dataset geodatabase logdir badattribute badattributecolumn

QA a CSCL dataset

positional arguments:
  dataset             Dataset name in cscl
  geodatabase         Path to the cscl geodatabase version
  logdir              Folder for logs
  badattribute        Known junk value (ex junk)
  badattributecolumn  Column to check for junk

options:
  -h, --help          show this help message and exit
```


### QA a child replica dataset

Report bad counts and (optionally) suspect values in a parent-child dataset pair.

```text
usage: qa_child_dataset.py [-h] [--badattribute BADATTRIBUTE] [--badattributecolumn BADATTRIBUTECOLUMN]
                           [--deltastart DELTASTART] [--childdataset CHILDDATASET]
                           dataset geodatabase childgeodatabase logdir

QA a child CSCL dataset

positional arguments:
  dataset               Dataset name in cscl
  geodatabase           Path to the parent cscl geodatabase
  childgeodatabase      Path to the child cscl geodatabase
  logdir                Folder for logs

options:
  -h, --help            show this help message and exit
  --badattribute BADATTRIBUTE
                        Known junk value (ex junk)
  --badattributecolumn BADATTRIBUTECOLUMN
                        Column to check for junk
  --deltastart DELTASTART
                        Known count difference on the child
  --childdataset CHILDDATASET
                        Name of child dataset if namespace is different from parent
```

### QA ZIP Codes

This script is not polished and (for now) must be run manually. The output is printout to the screen and a file geodatabase with suspect address point clusters.

It uses the well-known [DBSCAN](https://en.wikipedia.org/wiki/DBSCAN) algorithm to find ZIP code values that are not in a single cluster. It accepts as input either AddressPoint or Centerline.

The number of points required to form a cluster and the distance are configurable in the call to arcpy.stats.DensityBasedClustering. These are hard coded for now. If the input is centerlines we call GeneratePointsAlongLines with hard coded inputs.

Also hard coded in the script is a list of known multi-cluster ZIP codes like lower Manhattan plus Governor's Island. This should be improved.

```sh
> geodatabase-scripts\sample-qa-zipcode.bat
```


### Tests

Update the environmentals if necessary.

```sh
> geodatabase-scripts\testall.bat
```
