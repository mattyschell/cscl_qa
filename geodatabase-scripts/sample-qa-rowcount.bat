REM This is a sample for standalone testing.
REM You might want to see what rowcount QA is going to do.
REM But typically row count QA is called from cscl python scripts
REM  as a gate before doing something else like publishing
setlocal
set CSCLGDB=X:\path\to\cscl.gdb
set BASEPATH=X:\gis
set TARGETLOGDIR=%BASEPATH%\cscl_qa\geodatabase-scripts\logs\cscl_qa
set LOGNAME=sample-cscl-qa-rowcount
set NOTIFY=xxx@xxx.xxx
set NOTIFYFROM=xxx@xxx.xxx
set SMTPFROM=xxxxxxxxxx.xxxxxx
set PYTHON1=C:\Progra~1\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
set PYTHON2=C:\Users\%USERNAME%\AppData\Local\Programs\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
set BATLOG=%TARGETLOGDIR%\%LOGNAME%.log
echo QAing row counts on %CSCLGDB% on %date% at %time% 
REM This is the call here
REM This uses default counts in py\resources\rowcountrange
REM In real calls this resource lives in the scripts directory, not the repo
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_row_count.py %CSCLGDB% %TARGETLOGDIR% %LOGNAME% w
if %ERRORLEVEL% NEQ 0 (
    echo. >> %BATLOG%
    echo QA fail sending notification >> %BATLOG%
    CALL %PROPY% %BASEPATH%\cscl_qa\py\notify.py ^
                 "QA Report for row counts on %CSCLGDB%" ^
                 %NOTIFY% ^
                 %LOGNAME% ^
                 %TARGETLOGDIR% ^
                 %NOTIFYFROM% ^
                 %SMTPFROM%
    endlocal & EXIT /B 1
) 
echo done QAing row counts on %CSCLGDB% on %date% at %time%
endlocal & EXIT /B 0