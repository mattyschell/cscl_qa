rem this is the read only input
rem probably best to extract to a file geodatabase
rem but live CSCL should work too (untested)
set ADDRESSPOINT="C:\Temp\zipzza\cscl_addresspoint_xtract.gdb\AddressPoint"
rem you must manually create an empty scratch geodatabase
set SCRATCHGDB="C:\Temp\zipzza\scratch.gdb"
rem you must manually create an emtpy output geodatabase
set PROBLEMGDB="C:\Temp\zipzza\problem_zip_points.gdb"
set BASEPATH=C:\gis
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
echo QAing %ADDRESSPOINT% ZIP codes on %date% at %time% 
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_addresspoint_zips.py %ADDRESSPOINT% %SCRATCHGDB% %PROBLEMGDB%
echo done QAing %ADDRESSPOINT% ZIP codes on %date% at %time%
   