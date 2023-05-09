cmake_minimum_required(VERSION 3.21)
project(OpenAssetIO-Test-Conan)

enable_testing()
set(CMAKE_CXX_STANDARD 17)

#-----------------------------------------------------------------------
# Options

option(OPENASSETIOTEST_ENABLE_PYTHON "Test Python bindings" ON)

if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND
    CMAKE_CXX_COMPILER_VERSION VERSION_GREATER_EQUAL 5.0)
    option(OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI "For gcc, use the new C++11 library ABI" OFF)
endif ()

#-----------------------------------------------------------------------
# OpenAssetIO dependency.
find_package(OpenAssetIO REQUIRED)

# For Windows tests to work we must add the dlls to the PATH
if (WIN32 AND DEFINED OpenAssetIO_BINARY_DIR)
    file(TO_NATIVE_PATH "${OpenAssetIO_BINARY_DIR}" OpenAssetIO_BINARY_DIR_NATIVE)
endif ()

#-----------------------------------------------------------------------
# C++ tests.

add_executable(test.cpp.core test.core.cpp)
add_test(cpp.core test.cpp.core)
target_link_libraries(test.cpp.core PRIVATE OpenAssetIO::openassetio-core)

# GCC's C++11 ABI toggle must match OpenAssetIO's settings.
if (DEFINED OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI)
    if (OPENASSETIOTEST_GLIBCXX_USE_CXX11_ABI)
        target_compile_definitions(test.cpp.core PRIVATE _GLIBCXX_USE_CXX11_ABI=1)
    else ()
        target_compile_definitions(test.cpp.core PRIVATE _GLIBCXX_USE_CXX11_ABI=0)
    endif ()
endif ()

if (WIN32 AND DEFINED OpenAssetIO_BINARY_DIR)
    set_tests_properties(cpp.core PROPERTIES ENVIRONMENT "PATH=${OpenAssetIO_BINARY_DIR_NATIVE}")
endif ()

#-----------------------------------------------------------------------
# Python tests.

if (OPENASSETIOTEST_ENABLE_PYTHON)
    find_package(Python COMPONENTS Interpreter Development.Embed REQUIRED)

    #-----------------------------------------------------------------------
    # Python sources tests.

    # Python sources test.
    # -s - ignore the user site-directory (avoid unexpected things
    # leaking in).
    add_test(NAME python COMMAND ${Python_EXECUTABLE} -s ${PROJECT_SOURCE_DIR}/test.py)
    set_tests_properties(python PROPERTIES ENVIRONMENT PYTHONPATH=${OpenAssetIO_Python_SITELIB})

    #-----------------------------------------------------------------------
    # Python bridge test (loading Python plugin system from C++).

    add_executable(test.python.bridge test.python.bridge.cpp)
    add_test(python.bridge.cpp test.python.bridge)
    target_link_libraries(
        test.python.bridge
        PRIVATE
        OpenAssetIO::openassetio-python-bridge
        Python::Python
    )
    target_compile_features(test.python.bridge PRIVATE cxx_std_17)
    # If libpython is linked in as a static library, then we must export
    # symbols for dynamically loaded Python extension modules to use.
    set_target_properties(test.python.bridge PROPERTIES ENABLE_EXPORTS ON)

    # Storage for list of environment variables to set before running
    # the test.
    set(_envvars)

    # Add location of Python sources in the OpenAssetIO package to the
    # PYTHONPATH.
    list(APPEND _envvars "PYTHONPATH=${OpenAssetIO_Python_SITELIB}")

    # The test has an embedded Python interpreter, but is missing all
    # the required basic Python libraries, so we need to set PYTHONHOME
    # to the source Python package to avoid nasty errors.
    execute_process(
        COMMAND ${Python_EXECUTABLE} -c "import sys; sys.stdout.write(sys.prefix)"
        OUTPUT_VARIABLE Python_PREFIX
    )
    list(APPEND _envvars "PYTHONHOME=${Python_PREFIX}")

    # Fix library search path on MacOS.
    if (APPLE)
        # The `Python::Python` target's link options are set to e.g
        # `@rpath/Python.framework/Versions/3.9/Python` but all our
        # target's (CMake generated) @rpaths already contain
        # `Python.framework/Versions/3.9`. So add another RPATH with
        # the framework subdirectories stripped. This then allows our
        # test target to find the Python library.
        set_target_properties(test.python.bridge PROPERTIES BUILD_RPATH ${Python_PREFIX}/../../..)
    endif ()

    # Augment the PATH on Windows to find Python library dlls.
    if (WIN32)
        if (DEFINED OpenAssetIO_BINARY_DIR)
            list(APPEND _envvars.path ${OpenAssetIO_BINARY_DIR_NATIVE})
        endif ()
        foreach (path ${Python_RUNTIME_LIBRARY_DIRS})
            file(TO_NATIVE_PATH "${path}" path_native)
            list(APPEND _envvars.path ${path_native})
        endforeach ()
        # Frustratingly, $<SEMICOLON> doesn't work here, we have to find
        # the magic number of backslashes instead.
        list(JOIN _envvars.path \\\; _envvars.path)
        list(APPEND _envvars "PATH=${_envvars.path}")
    endif ()

    set_tests_properties(python.bridge.cpp PROPERTIES ENVIRONMENT "${_envvars}")
endif ()
