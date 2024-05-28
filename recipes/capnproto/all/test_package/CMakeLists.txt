cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(CapnProto REQUIRED capnp capnp-rpc CONFIG)


add_executable(addressbook test_package.c++ ${addressbookSources})
target_include_directories(addressbook PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(addressbook PRIVATE CapnProto::capnp)
target_compile_features(addressbook PRIVATE cxx_std_14)

