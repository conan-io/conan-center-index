cmake_minimum_required(VERSION 2.8.11)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c ${CONAN_LIBS})
set_property(TARGET test_package_c PROPERTY LINKER_LANGUAGE CXX)

add_executable(test_package_cpp test_package.cpp)
target_link_libraries(test_package_cpp ${CONAN_LIBS})
set_property(TARGET test_package_cpp PROPERTY CXX_STANDARD 11)
