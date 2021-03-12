@echo off

set BUILD=no

for %%i in (%*) do (

    if %%i==--build set BUILD=yes
)


if %BUILD%==yes (

cmake %*

) else (

emcmake cmake ^
      %*

)
