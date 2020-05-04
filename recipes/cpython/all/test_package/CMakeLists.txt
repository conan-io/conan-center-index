cmake_minimum_required(VERSION 2.8.11)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

set(CACHE PY_MAJOR "" CACHE STRING "Major version of python")
set(CACHE PY_VERSION "" CACHE STRING "Required version of python")

set(Python_ADDITIONAL_VERSIONS ${PY_VERSION} ${PY_MAJOR})

find_package(PythonInterp REQUIRED)
find_package(PythonLibs REQUIRED)

string(FIND "${PYTHON_EXECUTABLE}" "${CONAN_CPYTHON_ROOT}" ROOT_SUBPOS)
if(ROOT_SUBPOS EQUAL -1)
    message(FATAL_ERROR "found wrong python interpreter: ${PYTHON_EXECUTABLE}")
endif()

message(STATUS "PYTHON_VERSION_STRING: ${PYTHON_VERSION_STRING}")
message(STATUS "PYTHONLIBS_VERSION_STRING: ${PYTHONLIBS_VERSION_STRING}")
message(STATUS "PYTHON_LIBRARIES: ${PYTHON_LIBRARIES}")
message(STATUS "PYTHON_INCLUDE_PATH: ${PYTHON_INCLUDE_PATH}")

if(NOT PYTHON_VERSION_STRING AND NOT PYTHONLIBS_VERSION_STRING)
    message(FATAL_ERROR "Version of python interpreter and libraries not found")
endif()

if(PYTHON_VERSION_STRING)
    if(NOT PYTHON_VERSION_STRING STREQUAL "${PY_VERSION}")
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

if(CMAKE_VERSION VERSION_LESS "3.12" OR (MSVC AND CONAN_SETTINGS_BUILD_TYPE STREQUAL "Debug"))
    add_library(spam MODULE test_module.c)
    target_include_directories(spam
        PRIVATE
            ${PYTHON_INCLUDE_DIR}
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
else()
    find_package(Python${PY_MAJOR} REQUIRED COMPONENTS Interpreter Development)
    message("Python${PY_MAJOR}_EXECUTABLE: ${Python${PY_MAJOR}_EXECUTABLE}")
    message("Python${PY_MAJOR}_INTERPRETER_ID: ${Python${PY_MAJOR}_INTERPRETER_ID}")
    message("Python${PY_MAJOR}_VERSION: ${Python${PY_MAJOR}_VERSION}")
    message("Python${PY_MAJOR}_INCLUDE_DIRS: ${Python${PY_MAJOR}_INCLUDE_DIRS}")
    if(NOT Python${PY_MAJOR}_VERSION STREQUAL "${PYTHON_EXACT_VERSION}")
        message("Python_ADDITIONAL_VERSIONS does not match PYTHON_VERSION_STRING")
        message(FATAL_ERROR "CMake detected wrong cpython version")
    endif()

    if(PY_MAJOR STREQUAL "2")
        python2_add_library(spam "py${PY_MAJOR}/test_module.c")
    elseif(PY_MAJOR STREQUAL "3")
        python3_add_library(spam "py${PY_MAJOR}/test_module.c")
    else()
        message(FATAL_ERROR "Unknown PY_MAJOR")
    endif()
endif()

add_executable(${PROJECT_NAME} "py${PY_MAJOR}/test_package.c")
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
