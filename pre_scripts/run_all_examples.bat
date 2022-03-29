SET /A err = 0

CALL convert_notebooks.bat

set "your_dir=../axiomapy/examples"
pushd %cd%
cd %your_dir%


python with_sessions.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_sessions Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

python with_instruments.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_instruments Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

python with_positions.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_positions Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

python with_portfolios.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_portfolios Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

python with_analysis_definitions.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_analysis_definitions Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

python with_analyses.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_analyses Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

python with_instrument_analyses.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_instrument_analyses Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

python with_entitybase.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_entitybase Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

python with_blueapi.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_blueapi Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)


python with_risk_model_analyses.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_risk_model_analyses Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)


python with_marketdatasources.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_marketdatasources Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)


python with_async_analyses.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_async_analyses Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)


python with_datamart_jobs.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO with_datamart_jobs Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)



python with_performance_analyses.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO getting_started Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

python getting_started.py

IF %ERRORLEVEL% NEQ 0 ( 
   ECHO getting_started Failed %ERRORLEVEL%
   SET /A err = %ERRORLEVEL%
   GOTO EXIT_HERE
)

ECHO All Finished OK

:EXIT_HERE
ECHO Ending with code %err%
popd
EXIT /B %err% 
