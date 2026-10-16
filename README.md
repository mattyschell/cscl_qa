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

This script is not polished and (for now) must be run manually. The output is printout to the screen and a file geodatabase at py\resources\problem.gdb populated with suspect clusters.

We use the well-known [DBSCAN](https://en.wikipedia.org/wiki/DBSCAN) algorithm to identify ZIP code values that are not in a single cluster. We accept as input either AddressPoint or Centerline. If the input is Centerline we call GeneratePointsAlongLines with hard coded values.

The number of points required to form a cluster and the scan distance are configurable. If not configured these variables default to good known values. 

Several ZIP codes are legit multi-cluster ZIP codes like lower Manhattan plus Governor's Island. These ZIP codes get a reprieve from QA via the list in py\resources\multiclusterzipcodes.  

#### QA ZIP Codes: Sample Batch File

To run from a batch file update the values here:

```sh
> geodatabase-scripts\sample-qa-zipcode.bat
```

#### QA ZIP Codes: Ignore This Stuff

Ignore these warnings. 

This indicates a spatially tiny ZIP code. The algorithm will auto-shrink appropriately.  

```
WARNING 110018: The Neighborhood Distance can not exceed 75 percent of the maximum extent... setting the Neighborhood Distance to: xxxxx feet.
```

This indicates a numerically tiny ZIP code. The algorithm will ignore appropriately.  

```
Skipping ZIP 12345: Only 2 point
```

#### QA ZIP Codes: Review output

See [this companion document](doc/AddressPoint_ZipCode.md) for visual review tips.

### QA Overlaps

Some polygon feature classes should not allow overlapping polygons within the feature class.  City Council Districts come to mind.

See this sample script to QA one feature class and report overlaps.

```sh
> geodatabase-scripts\sample-qa-overlap.bat
```

### QA Row Counts

Sanity check that the big datasets have not been gutted or duplicated. Limits live in py\resources\rowcountrange (cscl) and py\resources\rowcountrange_pub (cscl_pub, pass via `--rowcountrange`) as `dataset minimum maximum` lines, set at roughly 90 and 110 percent of normal so only catastrophic change trips QA. Bump them as the data grows.

```text
usage: qa_row_count.py [-h] [--owner OWNER] [--rowcountrange ROWCOUNTRANGE] geodatabase logdir logname logmode
```

Use `--owner CSCL` against an enterprise geodatabase. The prd and stg replace-cscl*-gdb.bat scripts call qa-rowcount.bat or qa-pub-rowcount.bat first and stop publishing on failure.

### Tests

Update the environmentals if necessary.

```sh
> geodatabase-scripts\testall.bat
```
