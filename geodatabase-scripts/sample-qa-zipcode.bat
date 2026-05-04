rem this is the read only input
rem probably best to extract to a file geodatabase
rem but live CSCL should work too (untested)
rem set CSCLFEATURECLASS="C:\gis\cscl_qa\scratch\zipcodeqa\cscl.gdb\AddressPoint"
set CSCLFEATURECLASS="C:\gis\cscl_qa\scratch\zipcodeqa\cscl.gdb\CSCL\Centerline"
rem you must manually create an empty scratch geodatabase
set SCRATCHGDB="C:\gis\cscl_qa\scratch\zipcodeqa\scratch.gdb"
rem you must manually create an emptpy output geodatabase
set PROBLEMGDB="C:\gis\cscl_qa\scratch\zipcodeqa\problem_zip_points.gdb"
set BASEPATH=C:\gis
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
echo QAing %CSCLFEATURECLASS% ZIP codes on %date% at %time% 
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_addresspoint_zips.py %CSCLFEATURECLASS% %SCRATCHGDB% %PROBLEMGDB%
echo done QAing %CSCLFEATURECLASS% ZIP codes on %date% at %time%
   