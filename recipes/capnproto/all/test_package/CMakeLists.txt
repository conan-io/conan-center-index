cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(CapnProto REQUIRED capnp capnp-rpc CONFIG)

capnp_generate_cpp(addressbookSources addressbookHeaders addressbook.capnp)
add_executable(addressbook addressbook.c++ ${addressbookSources})
target_link_libraries(addressbook CapnProto::capnp)
target_include_directories(addressbook PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
set_property(TARGET addressbook PROPERTY CXX_STANDARD 14)

capnp_generate_cpp(calculatorSources calculatorHeaders calculator.capnp)
add_executable(calculator-client calculator-client.c++ ${calculatorSources})
add_executable(calculator-server calculator-server.c++ ${calculatorSources})
target_link_libraries(calculator-client CapnProto::capnp-rpc)
target_link_libraries(calculator-server CapnProto::capnp-rpc)
target_include_directories(calculator-client PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_include_directories(calculator-server PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
set_property(TARGET calculator-client PROPERTY CXX_STANDARD 14)
set_property(TARGET calculator-server PROPERTY CXX_STANDARD 14)
