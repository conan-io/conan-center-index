cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS NO_OUTPUT_DIRS)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}>)

find_package(SWIG REQUIRED)
include(UseSWIG)

find_package (Python3 COMPONENTS Interpreter Development)

enable_testing()

if(Python3_FOUND AND Python3_Interpreter_FOUND)
    swig_add_library(${PROJECT_NAME}
        LANGUAGE python
        SOURCES
            test.i
            test_package.c
    )

    get_filename_component(Python3_LIBRARY_DIR "${Python3_LIBRARIES}" DIRECTORY)

    message(STATUS "Python3_INCLUDE_DIRS: ${Python3_INCLUDE_DIRS}")
    message(STATUS "Python3_LIBRARIES: ${Python3_LIBRARIES}")
    message(STATUS "Python3_LIBRARY_DIR: ${Python3_LIBRARY_DIR}")

    target_link_libraries(_${PROJECT_NAME} PRIVATE Python3::Module)

    add_test(
        NAME gcd_test
        COMMAND ${Python3_EXECUTABLE} -c "import PackageTest; assert PackageTest.gcd(12, 16) == 4"
        WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
    )
    add_test(
        NAME foo_test
        COMMAND ${Python3_EXECUTABLE} -c "import PackageTest; assert PackageTest.cvar.foo == 3.14159265359"
        WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
    )
else()
    message(STATUS "Not building swig python module")
endif()
