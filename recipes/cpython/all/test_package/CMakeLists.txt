cmake_minimum_required(VERSION 3.1)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

set(CACHE PY_VERSION_MAJOR "" CACHE STRING "MAJOR version of python")
set(CACHE PY_VERSION_MAJOR_MINOR "" CACHE STRING "MAJOR.MINOR version of python")
set(CACHE PY_VERSION "" CACHE STRING "Required version of python")
set(CACHE PY_VERSION_SUFFIX "" CACHE STRING "Suffix of python")

set(Python_ADDITIONAL_VERSIONS ${PY_VERSION}${PY_VERSION_SUFFIX} ${PY_VERSION_MAJOR_MINOR}${PY_VERSION_SUFFIX} ${PY_VERSION_MAJOR}${PY_VERSION_SUFFIX} ${PY_VERSION} ${PY_VERSION_MAJOR_MINOR} ${PY_VERSION_MAJOR})
message("Using Python_ADDITIONAL_VERSIONS: ${Python_ADDITIONAL_VERSIONS}")

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)

string(FIND "${PYTHON_EXECUTABLE}" "${CONAN_CPYTHON_ROOT}" ROOT_SUBPOS)
if(ROOT_SUBPOS EQUAL -1)
    message(FATAL_ERROR "found wrong python interpreter: ${PYTHON_EXECUTABLE}")
endif()

message(STATUS "FindPythonInterp:")
message(STATUS "PYTHON_VERSION_STRING: ${PYTHON_VERSION_STRING}")
message(STATUS "PYTHON_VERSION_MAJOR: ${PYTHON_VERSION_MAJOR}")
message(STATUS "PYTHON_VERSION_MINOR: ${PYTHON_VERSION_MINOR}")
message(STATUS "PYTHON_VERSION_PATCH: ${PYTHON_VERSION_PATCH}")
message(STATUS "=============================================")
message(STATUS "FindPythonLibs:")
message(STATUS "PYTHON_LIBRARIES: ${PYTHON_LIBRARIES}")
message(STATUS "PYTHON_INCLUDE_PATH: ${PYTHON_INCLUDE_PATH} (deprecated)")
message(STATUS "PYTHON_INCLUDE_DIRS: ${PYTHON_INCLUDE_DIRS}")
message(STATUS "PYTHON_DEBUG_LIBRARIES: ${PYTHON_DEBUG_LIBRARIES} (deprecated)")
message(STATUS "PYTHONLIBS_VERSION_STRING: ${PYTHONLIBS_VERSION_STRING}")

if(NOT PYTHON_VERSION_STRING AND NOT PYTHONLIBS_VERSION_STRING)
    message(FATAL_ERROR "Version of python interpreter and libraries not found")
endif()

if(PYTHON_VERSION_STRING)
    if(NOT PYTHON_VERSION_STRING VERSION_EQUAL "${PY_VERSION}")
        message("PYTHON_VERSION_STRING does not match PY_VERSION")
        message(FATAL_ERROR "CMake detected wrong cpython version")
    endif()
endif()

if(PYTHONLIBS_VERSION_STRING)
    if(NOT PYTHONLIBS_VERSION_STRING STREQUAL "${PY_FULL_VERSION}")
        message("PYTHONLIBS_VERSION_STRING does not match PY_FULL_VERSION")
        message(FATAL_ERROR "CMake detected wrong cpython version")
    endif()
endif()

option(BUILD_MODULE "Build python module")

if(BUILD_MODULE)
    add_library(spam MODULE "py${PY_VERSION_MAJOR}/test_module.c")
    target_include_directories(spam
        PRIVATE
            ${PYTHON_INCLUDE_DIRS}
    )
    target_link_libraries(spam PRIVATE
        ${PYTHON_LIBRARIES}
    )
    set_property(TARGET spam PROPERTY PREFIX "")
    if(MSVC)
        if(CONAN_SETTINGS_BUILD_TYPE STREQUAL "Debug")
            set(SUFFIX "_d.pyd")
        else()
            set(SUFFIX ".pyd")
        endif()
        set_property(TARGET spam PROPERTY SUFFIX "${SUFFIX}")
    endif()

    option(USE_FINDPYTHON_X "Use new-style FindPythonX module")
    if(USE_FINDPYTHON_X AND NOT (CMAKE_VERSION VERSION_LESS "3.16"))
        # Require CMake 3.16 because this version introduces Python${PY_VERSION_MAJOR}_FIND_ABI
        find_package(Python${PY_VERSION_MAJOR} REQUIRED COMPONENTS Interpreter Development)
        message("Python${PY_VERSION_MAJOR}_EXECUTABLE: ${Python${PY_VERSION_MAJOR}_EXECUTABLE}")
        message("Python${PY_VERSION_MAJOR}_INTERPRETER_ID: ${Python${PY_VERSION_MAJOR}_INTERPRETER_ID}")
        message("Python${PY_VERSION_MAJOR}_VERSION: ${Python${PY_VERSION_MAJOR}_VERSION}")
        message("Python${PY_VERSION_MAJOR}_INCLUDE_DIRS: ${Python${PY_VERSION_MAJOR}_INCLUDE_DIRS}")
        message("Python${PY_VERSION_MAJOR}_LIBRARIES: ${Python${PY_VERSION_MAJOR}_LIBRARIES}")
        if(NOT Python${PY_VERSION_MAJOR}_VERSION STREQUAL "${PY_VERSION}")
            message("Python_ADDITIONAL_VERSIONS does not match PY_VERSION")
            message(FATAL_ERROR "CMake detected wrong cpython version")
        endif()

        if(PY_VERSION_MAJOR STREQUAL "2")
            python2_add_library(spam2 "py${PY_VERSION_MAJOR}/test_module.c")
        elseif(PY_VERSION_MAJOR STREQUAL "3")
            python3_add_library(spam2 "py${PY_VERSION_MAJOR}/test_module.c")
        else()
            message(FATAL_ERROR "Unknown PY_VERSION_MAJOR")
        endif()
    endif()
endif()

add_executable(${PROJECT_NAME} "py${PY_VERSION_MAJOR}/test_package.c")
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
