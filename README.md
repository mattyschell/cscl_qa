# CSCL-QA

Miscellaneous quality assurance checks on NYC's top banana geodatabase.  Friends, this is our quality assurance of the top banana, our rules, the trick is never to be afraid.

### QA a child replica dataset

```text
usage: qa_child_dataset.py [-h] [--deltastart DELTASTART] dataset geodatabase childgeodatabase logdir

QA a child CSCL dataset

positional arguments:
  dataset               Dataset name in cscl
  geodatabase           Path to the parent cscl geodatabase
  childgeodatabase      Path to the child cscl geodatabase
  logdir                Folder for logs

options:
  -h, --help            show this help message and exit
  --deltastart DELTASTART
                        Known count difference on the child
```


### Tests

Update the environmentals if necessary.

```sh
> geodatabase-scripts\testall.bat
```
