cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(list_network list_network.c)
target_link_libraries(list_network ${CONAN_LIBS})
