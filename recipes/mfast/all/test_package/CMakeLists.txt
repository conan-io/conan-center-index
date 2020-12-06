cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

FASTTYPEGEN_TARGET(Test Test.xml)
add_executable(message_printer ${FASTTYPEGEN_Test_OUTPUTS} message_printer.cpp)

target_link_libraries(message_printer ${CONAN_LIBS})
