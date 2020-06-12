cmake_minimum_required(VERSION 2.8.12)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(NOT ROCKSDB_DLL)
    add_executable(test_package_cpp test_package.cpp)
    target_link_libraries(test_package_cpp ${CONAN_LIBS})
    set_property(TARGET test_package_cpp PROPERTY CXX_STANDARD 11)
endif()

add_executable(test_package_stable_abi test_package_stable_abi.cpp)
target_link_libraries(test_package_stable_abi ${CONAN_LIBS})
