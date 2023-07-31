cmake_minimum_required(VERSION 3.15)
project(PackageTest C)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}>)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}>)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY $<1:${CMAKE_BINARY_DIR}>)

find_package(SWIG REQUIRED)
include(UseSWIG)

find_package(Python COMPONENTS Interpreter Development)

enable_testing()

if(Python_Interpreter_FOUND AND Python_Development_FOUND)
    swig_add_library(${PROJECT_NAME}
        LANGUAGE python
        SOURCES
            test.i
            test_package.c
    )

    target_link_libraries(${PROJECT_NAME} PRIVATE Python::Python)

    add_test(
        NAME gcd_test
        COMMAND ${Python_EXECUTABLE} -c "import PackageTest; assert PackageTest.gcd(12, 16) == 4"
        WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
    )
    add_test(
        NAME foo_test
        COMMAND ${Python_EXECUTABLE} -c "import PackageTest; assert PackageTest.cvar.foo == 3.14159265359"
        WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
    )
else()
    message(WARNING "Not building a SWIG Python test module")
endif()
