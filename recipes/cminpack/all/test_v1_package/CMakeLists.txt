cmake_minimum_required(VERSION 3.1.2)
project(CMinPack-ConanV1-TestPackage C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(CMinpack REQUIRED CONFIG)

# This builds one of the original cminpack examples against
# both types of the library

add_executable(cminpack_test_double ../test_package/tchkderc.c)
target_link_libraries(cminpack_test_double PRIVATE cminpack::cminpack)

add_executable(cminpack_test_float ../test_package/tchkderc.c)
target_link_libraries(cminpack_test_float PRIVATE cminpack::cminpacks)
