@echo off
set currdir=%cd%

set proInstallPath=None
set proPythonEnv=None

REM for /f "tokens=2* skip=2" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\ESRI\ArcGISPro" /v InstallDir 2^> nul') do set proInstallPath=%%b
for /f "tokens=2* skip=2" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\ESRI\ArcGISPro" /v InstallDir /reg:64 2^> nul') do set proInstallPath=%%b
for /f "tokens=2* skip=2" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\ESRI\ArcGISPro" /v PythonCondaEnv /reg:64 2^> nul') do set proPythonEnv=%%b
if EXIST "%proInstallPath%bin\ArcGISPro.exe" goto :getPythonPath

for /f "tokens=2* skip=2" %%a in ('reg query "HKEY_CURRENT_USER\Software\ESRI\ArcGISPro" /v InstallDir /reg:64 2^> nul') do set proInstallPath=%%b
for /f "tokens=2* skip=2" %%a in ('reg query "HKEY_CURRENT_USER\Software\ESRI\ArcGISPro" /v PythonCondaEnv /reg:64 2^> nul') do set proPythonEnv=%%b
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
	set project_workspace=D:\Praktikanten\Hackenberg_Moritz\DTK-Workflow-test\Services_test
	set gdb=Services_test.gdb
	set input_srs=25832
	REM ### cellsize DTK25 = 1.25; DTK50 = 2.5; DTK100 = 5
	set cellsize=1.25
	set id=DTK_RP_2023-04-05
	set source_data=W:\dtk100\rp\2022-11-24
	
	REM ###LAYER COL###
	%pythonPath% ..\scripts\MDCS.py -i:..\Parameter\Config\DTK_Source_col.xml -p:%project_workspace%$workspace -p:%gdb%$gdbName -p:%input_srs%$srs -p:%cellsize%$cellsize -p:%id%$id -p:%source_data%$dataPath
	
	REM ###1-BIT LAYER###
	for %%e in (acke,babl,baum,brac,grau,grbr,haus,hrot,park,rebr,rot,schw,sebl,stge,stor,swtx,trup,utmg,viol,wald,watt,weis,wies) do (
	%pythonPath% ..\scripts\MDCS.py -i:..\Parameter\Config\DTK_Source.xml -p:%project_workspace%$workspace -p:%gdb%$gdbName -p:%input_srs%$srs -p:%cellsize%$cellsize -p:%id%$id -p:%source_data%$dataPath %%e$layer
	)
	goto :Endscript

:ShowError
	@echo "Error: Could not find ArcGIS Pro."
	pause

:Endscript
	pause


