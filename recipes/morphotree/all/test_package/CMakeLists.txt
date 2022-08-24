cmake_minimum_required(VERSION 3.10)

project(simple_morphotree)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(simple_morphotree test_package.cpp)
target_link_libraries(simple_morphotree ${CONAN_LIBS})

