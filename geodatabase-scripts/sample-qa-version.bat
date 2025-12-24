@echo off
set ENV=xxx
set BASEPATH=X:\xxx
set DB=xxxxxxx
set LOGDIR=%BASEPATH%\geodatabase-scripts\logs\cscl_qa
set LOGMODE=w
set CSCLLAYER1=xxxx.xxxxxxxxx
set QAVALUE1=""
set QACOLUMN1=xxxxxxxx
set CSCLLAYER2=xxxx.xxxxxxxxxx
set QAVALUE2=JUNK
set QACOLUMN2=xxxxxxxxx
set QAVERSION=XXXXXXXVERSION
set CSCLGDB=%BASEPATH%\Connections\oracle19c\%ENV%\CSCL-%DB%\xxxxxxxxxx_xxxversion.sde
set NOTIFY=xxxxxx@xxx.xxx
set NOTIFYFROM=xxxxx@xxx.xxx.xxx
set SMTPFROM=xxxxxxxxxx.xxxxxx
set PYTHON1=C:\Python27\ArcGIS10.7\python.exe
set PYTHON2=C:\Python27\ArcGIS10.8\python.exe
if exist "%PYTHON1%" (
    set PROPY=%PYTHON1%
) else if exist "%PYTHON2%" (
    set PROPY=%PYTHON2%
) 
set BATLOG=%LOGDIR%\%ENV%-%QAVERSION%.log
echo QAing %ENV% %CSCLLAYER1% on %date% at %time% > %BATLOG%
set FAILCOUNT=0
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_one_dataset.py ^
             %CSCLLAYER1% ^
             %CSCLGDB% ^
             %LOGDIR% ^
             QA-%QAVERSION% ^
             %LOGMODE% ^
             %QAVALUE1% ^
             %QACOLUMN1%  
if %ERRORLEVEL% NEQ 0 (
    set /a FAILCOUNT+=1
    echo. >> %BATLOG%
    echo QA fail for %CSCLLAYER1% >> %BATLOG%
) 
echo. >> %BATLOG% && echo completed %ENV% %CSCLLAYER1% on %date% at %time% >> %BATLOG%
echo QAing %ENV% %CSCLLAYER2% on %date% at %time% > %BATLOG%
set LOGMODE=a
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_one_dataset.py ^
             %CSCLLAYER2% ^
             %CSCLGDB% ^
             %LOGDIR% ^
             QA-%QAVERSION% ^
             %LOGMODE% ^
             %QAVALUE2% ^
             %QACOLUMN2%  
if %ERRORLEVEL% NEQ 0 (
    set /a FAILCOUNT+=1
    echo. >> %BATLOG%
    echo QA fail for %CSCLLAYER2% >> %BATLOG%
) 
echo. >> %BATLOG% && echo completed %ENV% %CSCLLAYER2% on %date% at %time% >> %BATLOG%
if %FAILCOUNT% GTR 0 (
    echo Sending combined QA notification >> %BATLOG%
    CALL %PROPY% %BASEPATH%\cscl_qa\py\notify.py "QA Report for %QAVERSION% (%ENV%)" %NOTIFY% QA-%QAVERSION% %LOGDIR% %NOTIFYFROM% %SMTPFROM%
    echo    .------.    .------.    .------.
    echo   /  STOP  \  /  STOP  \  /  STOP  \
    echo   \   QA   /  \   QA   /  \   QA   /
    echo    '------'    '------'    '------' 
)
if %FAILCOUNT% NEQ 0 (
    echo Check your email for QA details
    echo Continue without reconciling and posting %QAVERSION%
    echo Acknowledge you have seen this by
    pause
)
exit /b 0
   