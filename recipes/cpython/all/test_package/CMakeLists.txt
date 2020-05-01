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

if(NOT PYTHON_VERSION_STRING MATCHES "${Python_ADDITIONAL_VERSIONS}.*")
    message("Python_ADDITIONAL_VERSIONS does not match PYTHON_VERSION_STRING")
    message(FATAL_ERROR "CMake detected wrong cpython version")
endif()

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

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
