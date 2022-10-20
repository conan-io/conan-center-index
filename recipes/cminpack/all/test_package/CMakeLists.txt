cmake_minimum_required(VERSION 3.12)
project(CMinPack-Conan-TestPackage C)

find_package(CMinpack REQUIRED)

# This builds one of the original cminpack examples against
# both types of the library

add_executable(cminpack_test_double tchkderc.c)
target_link_libraries(cminpack_test_double PRIVATE cminpack::cminpack)

add_executable(cminpack_test_float tchkderc.c)
target_link_libraries(cminpack_test_float PRIVATE cminpack::cminpacks)
