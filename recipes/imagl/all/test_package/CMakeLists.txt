cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS})

if(STATIC_LIB)
    add_compile_definitions(IMAGL_STATIC)
endif()

set_property(TARGET example PROPERTY CXX_STANDARD 20)
set_property(TARGET example PROPERTY CXX_STANDARD_REQUIRED ON)

# CTest is a testing tool that can be used to test your project.
# enable_testing()
# add_test(NAME example
#          WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
#          COMMAND example)
