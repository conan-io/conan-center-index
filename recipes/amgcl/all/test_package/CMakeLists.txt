cmake_minimum_required(VERSION 3.1)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(solver solver.cpp)
target_link_libraries(solver ${CONAN_LIBS})
set_property(TARGET solver PROPERTY CXX_STANDARD 11)
