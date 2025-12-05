set ENV=dev
set BASEPATH=X:\gis
set LOGDIR=%BASEPATH%\cscl_qa\geodatabase-scripts\logs
set CSCLLAYER=CSCL.FeatureClass
set CSCLGDB=%BASEPATH%\Connections\oracle19c\%ENV%\CSCL-xxxxxxx\cscl_read_only.sde
REM fake stg to demo
set CHILDGDB=%BASEPATH%\Connections\oracle19c\stg\CSCL-xxxxxxx\cscl_read_only.sde
set DESCRIPTIVECHILDGDB=FAKE
set NOTIFY=xxx@xxx.xxx.xxx
set NOTIFYFROM=xxx@xxx.xxx.xxx
set SMTPFROM=xxxxxxxxx.xxxxxx
set PYTHON1=C:\Python27\ArcGIS10.7\python.exe
set PYTHON2=C:\Python27\ArcGIS10.8\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
set BATLOG=%LOGDIR%\%ENV%-%CSCLLAYER%.log
echo QAing %ENV% %CSCLLAYER% on %date% at %time% > %BATLOG%
REM exit 1 if QA 
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_child_dataset.py ^
             %CSCLLAYER% ^
             %CSCLGDB% ^
             %CHILDGDB% ^
             %LOGDIR% 
if %ERRORLEVEL% NEQ 0 (
    echo. >> %BATLOG%
    echo QA fail sending notification >> %BATLOG%
    CALL %PROPY% %BASEPATH%\cscl_qa\py\notify.py "QA Report for %CSCLLAYER% (%ENV%) on %DESCRIPTIVECHILDGDB%" %NOTIFY% qa-%CSCLLAYER% %LOGDIR% %NOTIFYFROM% %SMTPFROM%
    EXIT /B 0
) 
echo. >> %BATLOG% && echo completed %ENV% %CSCLLAYER% on %date% at %time% >> %BATLOG%
   