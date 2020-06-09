cmake_minimum_required(VERSION 3.16 FATAL_ERROR)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(executor ${PROJECT_SOURCE_DIR}/executor.cpp)

target_link_libraries(executor ${CONAN_LIBS})

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
