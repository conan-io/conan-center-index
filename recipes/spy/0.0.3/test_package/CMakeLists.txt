cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_library(spy_config INTERFACE)
target_compile_features ( spy_config INTERFACE  cxx_std_17 )

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS} PUBLIC spy_config)

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
