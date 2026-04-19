@echo off

echo =============================
echo Run 1: UNMARKED tests only
echo =============================
pytest -m "unmarked" --html=report_unmarked.html --self-contained-html
if %ERRORLEVEL% neq 0 echo Run 1 failed

echo =============================
echo Run 2: validate_csv tests
echo =============================
pytest -m "validate_csv" --html=report_validate_csv.html --self-contained-html
if %ERRORLEVEL% neq 0 echo Run 2 failed

echo =============================
echo Run 3: NOT xfail tests
echo =============================
pytest -m "not xfail" --html=report_not_xfail.html --self-contained-html
if %ERRORLEVEL% neq 0 echo Run 3 failed

echo =============================
echo Done
echo =============================
pause