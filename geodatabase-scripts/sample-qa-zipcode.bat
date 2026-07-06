rem this is the read only input
rem extract to a file geodatabase or download from arcgis online
rem live CSCL should work too (untested)
set CSCLFEATURECLASS="C:\gis\cscl_qa\scratch\zipcodeqa\cscl.gdb\AddressPoint"
rem set CSCLFEATURECLASS="C:\gis\cscl_qa\scratch\zipcodeqa\cscl.gdb\CSCL\Centerline"
set BASEPATH=C:\gis
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
echo QAing %CSCLFEATURECLASS% ZIP codes on %date% at %time% 
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_addresspoint_zips.py %CSCLFEATURECLASS% 
echo done QAing %CSCLFEATURECLASS% ZIP codes on %date% at %time%