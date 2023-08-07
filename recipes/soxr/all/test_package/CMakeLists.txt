cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

enable_testing()

find_package(soxr CONFIG REQUIRED)

add_executable(test_package_core test_package_core.c)
target_link_libraries(test_package_core soxr::core)
add_test(NAME test_package_core COMMAND test_package_core)

if(TARGET soxr::lsr)
    add_executable(test_package_lsr test_package_lsr.c)
    target_link_libraries(test_package_lsr soxr::lsr)
    add_test(NAME test_package_lsr COMMAND test_package_lsr)
endif()
