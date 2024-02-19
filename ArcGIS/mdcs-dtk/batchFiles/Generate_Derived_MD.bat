@echo off
set currdir=%cd%

set proInstallPath=None
set proPythonEnv=None

for /f "tokens=2* skip=2" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\ESRI\ArcGISPro" /v InstallDir 2^> nul') do set proInstallPath=%%b
for /f "tokens=2* skip=2" %%a in ('reg query "HKEY_CURRENT_USER\Software\ESRI\ArcGISPro" /v PythonCondaEnv') do set proPythonEnv=%%b
if EXIST "%proInstallPath%bin\ArcGISPro.exe" goto :getPythonPath

for /f "tokens=2* skip=2" %%a in ('reg query "HKEY_CURRENT_USER\Software\ESRI\ArcGISPro" /v InstallDir') do set proInstallPath=%%b
for /f "tokens=2* skip=2" %%a in ('reg query "HKEY_CURRENT_USER\Software\ESRI\ArcGISPro" /v PythonCondaEnv') do set proPythonEnv=%%b
if EXIST "%proInstallPath%bin\ArcGISPro.exe" goto :getPythonPath
goto :ShowError

:getPythonPath
	echo %proInstallPath%
	echo %proPythonEnv% 
			
	if NOT EXIST %proPythonEnv% (
		set pythonPath="%proInstallPath%bin\Python\envs\arcgispro-py3\python.exe" 		
		goto :ProStuff
	)

	set pythonPath=%proPythonEnv%\python.exe
	goto :ProStuff
	

:ProStuff

	%pythonPath% ..\scripts\MDCS.py -i:..\Parameter\config\D_Preprocessed.xml
	goto :Endscript

:ShowError
	@echo "Error: Could not find ArcGIS."
	pause

:Endscript
	pause