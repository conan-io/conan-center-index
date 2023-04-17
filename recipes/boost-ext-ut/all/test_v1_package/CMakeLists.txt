cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(ut REQUIRED CONFIG)

set(namespace Boost)
if(ut_VERSION VERSION_LESS "1.1.9")
  set(namespace boost)
endif()

add_executable(test_package ../test_package/test_package.cpp)
target_link_libraries(test_package PRIVATE "${namespace}::ut")
target_compile_features(test_package PRIVATE cxx_std_20)
