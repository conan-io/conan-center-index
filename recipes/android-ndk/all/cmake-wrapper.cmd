@echo off

set BUILD=no

for %%i in (%*) do (

    if %%i==--build set BUILD=yes
)


if %BUILD%==yes (

cmake %*

) else (

REM https://gitlab.kitware.com/cmake/cmake/issues/18739 Android: NDK r19 support
REM https://github.com/conan-io/conan/issues/2402 Android and CONAN_LIBCXX do not play well together
REM https://github.com/conan-io/conan/issues/4537 Pass ANDROID_ABI & ANDROID_NDK variables to cmake
REM https://github.com/conan-io/conan/issues/4629 set(CMAKE_FIND_ROOT_PATH_MODE_* ONLY) when cross-compiling, for Android at least

cmake ^
      -DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=%CMAKE_FIND_ROOT_PATH_MODE_PROGRAM% ^
      -DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=%CMAKE_FIND_ROOT_PATH_MODE_LIBRARY% ^
      -DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=%CMAKE_FIND_ROOT_PATH_MODE_INCLUDE% ^
      -DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=%CMAKE_FIND_ROOT_PATH_MODE_PACKAGE% ^
      -DANDROID_STL=%ANDROID_STL% ^
      -DANDROID_NDK=%ANDROID_NDK% ^
      -DANDROID_ABI=%ANDROID_ABI% ^
      -DANDROID_PLATFORM=%ANDROID_PLATFORM% ^
      -DANDROID_TOOLCHAIN=%ANDROID_TOOLCHAIN% ^
      -DANDROID_NATIVE_API_LEVEL=%ANDROID_NATIVE_API_LEVEL% ^
      %*

)
