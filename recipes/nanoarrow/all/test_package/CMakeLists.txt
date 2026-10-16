cmake_minimum_required(VERSION 3.14)
project(test_package C)

find_package(nanoarrow REQUIRED)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE nanoarrow::nanoarrow)
if(NANOARROW_TEST_WITH_IPC)
  target_link_libraries(test_package PRIVATE nanoarrow::nanoarrow_ipc)
  target_compile_definitions(test_package PRIVATE NANOARROW_TEST_WITH_IPC)
endif()
