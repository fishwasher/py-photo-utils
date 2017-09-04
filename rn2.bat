@echo off
REM Parameters:
REM target directory (optional, defaults to current, use '-' for default if second parameter is present)
REM time shift (e.g. '-1:33') if file time is offset
python rename2.py %1 %2