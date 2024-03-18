cmake_minimum_required(VERSION 3.15)
project(test_package C)

find_package(cpython REQUIRED CONFIG)

# FIXME: We can't modify CMake's FindPython to link dependencies pulled by
# Conan, so here we just include them globally. This is mainly necessary for
# MacOS missing crypt.h, which is available at configure time (in the main recipe)
# but otherwise not at build time (in consumer packages).
link_libraries(cpython::python)

set(PY_VERSION_MAJOR_MINOR "" CACHE STRING "MAJOR.MINOR version of python")
set(PY_VERSION "" CACHE STRING "Required version of python")
set(PY_VERSION_SUFFIX "" CACHE STRING "Suffix of python")

set(Python_ADDITIONAL_VERSIONS ${PY_VERSION}${PY_VERSION_SUFFIX} ${PY_VERSION_MAJOR_MINOR}${PY_VERSION_SUFFIX} 3${PY_VERSION_SUFFIX} ${PY_VERSION} ${PY_VERSION_MAJOR_MINOR} 3)
message("Using Python_ADDITIONAL_VERSIONS: ${Python_ADDITIONAL_VERSIONS}")

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)

string(FIND "${PYTHON_EXECUTABLE}" "${CONAN_CPYTHON_ROOT}" ROOT_SUBPOS)
if(ROOT_SUBPOS EQUAL -1)
    message(FATAL_ERROR "found wrong python interpreter: ${PYTHON_EXECUTABLE}")
endif()

message(STATUS "FindPythonInterp:")
message(STATUS "PYTHON_VERSION_STRING: ${PYTHON_VERSION_STRING}")
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
    if(NOT PYTHONLIBS_VERSION_STRING STREQUAL "${PY_VERSION}")
        message("PYTHONLIBS_VERSION_STRING does not match PY_VERSION")
        message(FATAL_ERROR "CMake detected wrong cpython version")
    endif()
endif()

option(BUILD_MODULE "Build python module")

if(BUILD_MODULE)
    add_library(spam MODULE "test_module.c")
    target_include_directories(spam
        PRIVATE
            ${PYTHON_INCLUDE_DIRS}
    )
    target_link_libraries(spam PRIVATE
        ${PYTHON_LIBRARIES}
    )
    set_property(TARGET spam PROPERTY PREFIX "")
    if(MSVC)
        set_target_properties(spam PROPERTIES 
            DEBUG_POSTFIX "_d"
            SUFFIX ".pyd"
        )
    endif()

    option(USE_FINDPYTHON_X "Use new-style FindPythonX module")
    if(USE_FINDPYTHON_X AND NOT CMAKE_VERSION VERSION_LESS "3.16")
        # Require CMake 3.16 because this version introduces Python3_FIND_ABI
        find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
        message("Python3_EXECUTABLE: ${Python3_EXECUTABLE}")
        message("Python3_INTERPRETER_ID: ${Python3_INTERPRETER_ID}")
        message("Python3_VERSION: ${Python3_VERSION}")
        message("Python3_INCLUDE_DIRS: ${Python3_INCLUDE_DIRS}")
        message("Python3_LIBRARIES: ${Python3_LIBRARIES}")
        if(NOT Python3_VERSION STREQUAL "${PY_VERSION}")
            message("Python_ADDITIONAL_VERSIONS does not match PY_VERSION")
            message(FATAL_ERROR "CMake detected wrong cpython version")
        endif()

        python3_add_library(spam2 "test_module.c")
    endif()
endif()

add_executable(${PROJECT_NAME} "test_package.c")
target_link_libraries(${PROJECT_NAME} PRIVATE cpython::embed)
