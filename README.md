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


### Tests

Update the environmentals if necessary.

```sh
> geodatabase-scripts\testall.bat
```
