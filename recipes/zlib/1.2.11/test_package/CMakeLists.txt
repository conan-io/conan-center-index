cmake_minimum_required(VERSION 3.0)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(test_zlib test.c)
target_link_libraries(test_zlib CONAN_PKG::zlib)
set_target_properties(test_zlib PROPERTIES OUTPUT_NAME "test")

if(WITH_MINIZIP)
  add_executable(test_minizip test_minizip.c)
  target_link_libraries(test_minizip CONAN_PKG::zlib)
endif()
