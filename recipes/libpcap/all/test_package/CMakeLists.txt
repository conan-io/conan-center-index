cmake_minimum_required(VERSION 3.1)
project(libpcap_example)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(list_network list_network.c)
target_link_libraries(list_network ${CONAN_LIBS})
