cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS})
target_compile_features(example PRIVATE cxx_std_17)
