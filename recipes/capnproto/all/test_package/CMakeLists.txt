cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(CapnProto REQUIRED capnp capnp-rpc CONFIG)

capnp_generate_cpp(addressbookSources addressbookHeaders addressbook.capnp)
add_executable(addressbook addressbook.c++ ${addressbookSources})
target_include_directories(addressbook PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(addressbook PRIVATE CapnProto::capnp)
target_compile_features(addressbook PRIVATE cxx_std_14)

capnp_generate_cpp(calculatorSources calculatorHeaders calculator.capnp)
add_library(calculator_protocol STATIC ${calculatorSources})
target_include_directories(calculator_protocol PUBLIC ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(calculator_protocol PUBLIC CapnProto::capnp-rpc)
target_compile_features(calculator_protocol PUBLIC cxx_std_14)

add_executable(calculator-client calculator-client.c++)
target_link_libraries(calculator-client PRIVATE calculator_protocol)
add_executable(calculator-server calculator-server.c++)
target_link_libraries(calculator-server PRIVATE calculator_protocol)
