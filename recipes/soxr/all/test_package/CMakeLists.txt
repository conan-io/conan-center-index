cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(soxr CONFIG REQUIRED)

add_executable(test_package_core test_package_core.c)
target_link_libraries(test_package_core soxr::core)

if(TARGET soxr::lsr)
    add_executable(test_package_lsr test_package_lsr.c)
    target_link_libraries(test_package_lsr soxr::lsr)
endif()
