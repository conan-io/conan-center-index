cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS})
set_target_properties(example PROPERTIES
    CXX_STANDARD 11 # Elfio requires at least c++11
    CXX_STANDARD_REQUIRED ON)
