set ENV=dev
set BASEPATH=X:\gis
set LOGDIR=%BASEPATH%\geodatabase-scripts\logs\cscl_qa
set CSCLLAYER=CSCL.FeatureClass
set QACOLUMN=SAMPLECOLUMN
set QAVALUE=whywasthe6scaredbecause789
set QAVERSION=CSCL.SPECIALVERSION
set CSCLGDB=%BASEPATH%\Connections\oracle19c\%ENV%\CSCL-xxxxx\cscl_read_only.sde
set NOTIFY=mschell@oti.nyc.gov
set NOTIFYFROM=mschell@oti.nyc.gov
set SMTPFROM=doittsmtp.nycnet
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
CALL %PROPY% %BASEPATH%\cscl_qa\py\qa_one_dataset.py ^
             %CSCLLAYER% ^
             %CSCLGDB% ^
             %LOGDIR% ^
             %QAVALUE% ^
             %QACOLUMN%  
if %ERRORLEVEL% NEQ 0 (
    echo. >> %BATLOG%
    echo QA fail sending notification >> %BATLOG%
    CALL %PROPY% %BASEPATH%\cscl_qa\py\notify.py "QA Report for %CSCLLAYER% (%ENV%)" %NOTIFY% qa-%CSCLLAYER%-%VERSION% %LOGDIR% %NOTIFYFROM% %SMTPFROM%
    EXIT /B 0
) 
echo. >> %BATLOG% && echo completed %ENV% %CSCLLAYER% on %date% at %time% >> %BATLOG%
   