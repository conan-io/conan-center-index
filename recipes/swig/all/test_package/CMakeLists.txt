cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS NO_OUTPUT_DIRS)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}>)

find_package(SWIG REQUIRED)
include(UseSWIG)

set(Python_ADDITIONAL_VERSIONS 3)
find_package(PythonInterp)
find_package(PythonLibs 3)

enable_testing()

if(PYTHONINTERP_FOUND AND PYTHONLIBS_FOUND)
    swig_add_library(${PROJECT_NAME}
        LANGUAGE python
        SOURCES
            test.i
            test_package.c
    )

    get_filename_component(PYTHON_LIBRARY_DIR "${PYTHON_LIBRARIES}" DIRECTORY)

    message(STATUS "PYTHON_INCLUDE_DIRS: ${PYTHON_INCLUDE_DIRS}")
    message(STATUS "PYTHON_LIBRARIES: ${PYTHON_LIBRARIES}")
    message(STATUS "PYTHON_LIBRARY_DIR: ${PYTHON_LIBRARY_DIR}")

    #target_compile_definitions(_${PROJECT_NAME} PRIVATE MS_NO_COREDLL)
    target_include_directories(_${PROJECT_NAME} PRIVATE ${PYTHON_INCLUDE_DIRS})
    target_link_directories(_${PROJECT_NAME} PRIVATE ${PYTHON_LIBRARY_DIR})
    target_link_libraries(_${PROJECT_NAME} PRIVATE ${PYTHON_LIBRARIES})

    add_test(
        NAME gcd_test
        COMMAND ${PYTHON_EXECUTABLE} -c "import PackageTest; assert PackageTest.gcd(12, 16) == 4"
        WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
    )
    add_test(
        NAME foo_test
        COMMAND ${PYTHON_EXECUTABLE} -c "import PackageTest; assert PackageTest.cvar.foo == 3.14159265359"
        WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
    )
else()
    message(STATUS "Not building swig python module")
endif()
