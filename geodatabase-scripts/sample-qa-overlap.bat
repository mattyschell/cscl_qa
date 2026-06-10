set CSCLLAYER=xxxxx
set BASEPATH=X:\xxx
set CSCLGDB=X:\xxx\xxx.gdb
rem expect some overlap. 1-10 square feet perhaps
rem alternatively take the existing overlap and QA when the number jumps
rem bear in mind that starting with 5 and the number jumping to 10 is NBD
set CSCLOVERLAPTOLERANCE=50
set LOGDIR=%BASEPATH%\geodatabase-scripts\logs\cscl_qa
set NOTIFY=xxx@xxx.xxx.xxx
set NOTIFYFROM=xxx@xxx.xxx.xxx
set SMTPFROM=xxxx.xxxxx
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
set BATLOG=%LOGDIR%\sample-qa-overlap.log
echo QAing %CSCLLAYER% for overlaps on %date% at %time% 
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_overlap.py %CSCLLAYER% %CSCLGDB% %LOGDIR% %CSCLLAYER%-qa-overlap w %CSCLOVERLAPTOLERANCE%
if %ERRORLEVEL% NEQ 0 (
    echo. >> %BATLOG%
    echo QA fail sending notification >> %BATLOG%
    CALL %PROPY% %BASEPATH%\cscl_qa\py\notify.py ^
                 "QA Report for %CSCLLAYER% overlap on %CSCLGDB%" ^
                 %NOTIFY% ^
                 %CSCLLAYER%-qa-overlap ^
                 %LOGDIR% ^
                 %NOTIFYFROM% ^
                 %SMTPFROM%
    EXIT /B 0
) 
echo done QAing %CSCLLAYER% for overlaps on on %date% at %time%
   