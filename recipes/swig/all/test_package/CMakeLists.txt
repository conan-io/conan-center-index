cmake_minimum_required(VERSION 3.1)
project(PackageTest C)
enable_testing()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(NO_OUTPUT_DIRS)

find_program(PYTHON_EXECUTABLE NAMES python3 python REQUIRED)
find_package(PythonLibs 3 REQUIRED)

find_package(SWIG REQUIRED)
include(UseSWIG)

swig_add_library(${PROJECT_NAME}
    LANGUAGE python
    SOURCES
        test.i
        test_package.c
)
target_include_directories(_${PROJECT_NAME} PRIVATE ${PYTHON_INCLUDE_DIRS})
target_link_libraries(_${PROJECT_NAME} PRIVATE ${PYTHON_LIBRARIES})

add_test(gcd_test ${PYTHON_EXECUTABLE} -c "import PackageTest; assert PackageTest.gcd(12, 16) == 4")
add_test(foo_test ${PYTHON_EXECUTABLE} -c "import PackageTest; assert PackageTest.cvar.foo == 3.14159265359")
