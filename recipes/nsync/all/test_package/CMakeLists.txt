cmake_minimum_required(VERSION 3.1)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example_c example_c.c)
target_link_libraries(example_c ${CONAN_LIBS_NSYNC})

add_executable(example_cpp example_cpp.cpp)
target_link_libraries(example_cpp ${CONAN_LIBS_NSYNC})

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
