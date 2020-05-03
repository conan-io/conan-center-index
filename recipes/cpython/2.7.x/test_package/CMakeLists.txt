cmake_minimum_required(VERSION 2.8.11)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

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
    if(NOT PYTHON_VERSION_STRING STREQUAL "${PYTHON_EXACT_VERSION}")
        message("PYTHON_VERSION_STRING does not match PYTHON_EXACT_VERSION")
        message(FATAL_ERROR "CMake detected wrong cpython version")
    endif()
endif()

if(PYTHONLIBS_VERSION_STRING)
    if(NOT PYTHONLIBS_VERSION_STRING STREQUAL "${PYTHON_EXACT_VERSION}")
        message("PYTHONLIBS_VERSION_STRING does not match PYTHON_EXACT_VERSION")
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
    find_package(Python2 REQUIRED COMPONENTS Interpreter Development)
    message("Python2_EXECUTABLE: ${Python2_EXECUTABLE}")
    message("Python2_INTERPRETER_ID: ${Python2_INTERPRETER_ID}")
    message("Python2_VERSION: ${Python2_VERSION}")
    message("Python2_INCLUDE_DIRS: ${Python2_INCLUDE_DIRS}")
    if(NOT Python2_VERSION STREQUAL "${PYTHON_EXACT_VERSION}")
        message("Python_ADDITIONAL_VERSIONS does not match PYTHON_VERSION_STRING")
        message(FATAL_ERROR "CMake detected wrong cpython version")
    endif()

    python2_add_library(spam test_module.c)
endif()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
