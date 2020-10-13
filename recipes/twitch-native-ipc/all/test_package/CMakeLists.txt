cmake_minimum_required(VERSION 3.1)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_executable(example example.c)
target_link_libraries(example ${CONAN_LIBS})

add_executable(example2 example2.cpp)
target_link_libraries(example2 ${CONAN_LIBS})
target_compile_features(example2 PRIVATE cxx_std_17)
