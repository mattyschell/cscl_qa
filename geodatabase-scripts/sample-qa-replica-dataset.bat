set ENV=xxx
set BASEPATH=X:\xxx
set LOGDIR=%BASEPATH%\geodatabase-scripts\log\scscl_qa
set DB=xxxxxxx
set CSCLLAYER=xxxx.xxxxxxx
set CSCLGDB=%BASEPATH%\Connections\oracle19c\%ENV%\CSCL-%DB%\cscl_read_only.sde
set CHILDGDB=X:\REPLICATIONS\xxx\xxx.sde
set QACOLUMN=XXXXX_XXXX
set QAVALUE=XXXX
set DESCRIPTIVECHILDGDB=XXXX
set NOTIFY=xxxx@xxx.xxx.xxx
set NOTIFYFROM=xxxx@xxx.xxx.xxx
set SMTPFROM=xxxxx.xxxx
set PYTHON1=C:\Python27\ArcGIS10.7\python.exe
set PYTHON2=C:\Python27\ArcGIS10.8\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
set BATLOG=%LOGDIR%\%ENV%-%CSCLLAYER%.log
echo QAing %ENV% %CSCLLAYER% on %date% at %time% > %BATLOG%
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_child_dataset.py ^
             %CSCLLAYER% ^
             %CSCLGDB% ^
             %CHILDGDB% ^
             %LOGDIR% ^
             --badattributecolumn %QACOLUMN% ^
             --badattribute %QAVALUE%
if %ERRORLEVEL% NEQ 0 (
    echo. >> %BATLOG%
    echo QA fail sending notification >> %BATLOG%
    CALL %PROPY% %BASEPATH%\cscl_qa\py\notify.py "QA Report for %CSCLLAYER% (%ENV%) on %DESCRIPTIVECHILDGDB%" %NOTIFY% %CSCLLAYER% %LOGDIR% %NOTIFYFROM% %SMTPFROM%
    EXIT /B 0
) 
echo. >> %BATLOG% && echo completed %ENV% %CSCLLAYER% on %date% at %time% >> %BATLOG%
   