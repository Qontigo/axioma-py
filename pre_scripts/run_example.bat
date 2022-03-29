SET /A err = 0

CALL convert_notebooks.bat

set "your_dir=../axiomapy/examples"
pushd %cd%
cd %your_dir%



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
