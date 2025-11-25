set OLDPY7=C:\Python27\ArcGIS10.7\python.exe
set OLDPY8=C:\Python27\ArcGIS10.8\python.exe
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
if exist "%OLDPY7%" (
    set OLDPY=%OLDPY7%
) else if exist "%OLDPY8%" (
    set OLDPY=%OLDPY8%
) 
call %PROPY% .\py\test_cscl_dataset.py
call %OLDPY% .\py\test_cscl_dataset.py