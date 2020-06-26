cmake_minimum_required(VERSION 2.8.11)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

FASTTYPEGEN_TARGET(MDRefreshSample MDRefreshSample.xml)
add_executable (message_printer ${FASTTYPEGEN_MDRefreshSample_OUTPUTS} message_printer.cpp)

target_link_libraries(message_printer ${CONAN_LIBS})
