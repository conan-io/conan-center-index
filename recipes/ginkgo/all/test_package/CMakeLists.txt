cmake_minimum_required(VERSION 3.9)
project(test_install)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_install test_install.cpp)
target_link_libraries(test_install ${CONAN_LIBS})
set_target_properties(test_install PROPERTIES CXX_STANDARD 14)
