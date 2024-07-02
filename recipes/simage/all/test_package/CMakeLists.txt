cmake_minimum_required(VERSION 3.12)
project(test_package LANGUAGES CXX)

#test finding package via cmake
find_package(simage REQUIRED)

add_executable(test_cmake_find main.cpp)
target_link_libraries(test_cmake_find PUBLIC simage::simage)


#test finding package via pkg-config
include(FindPkgConfig)
pkg_check_modules(SIMAGEPC REQUIRED simage)

add_executable(test_pkc_find main.cpp)
target_link_libraries(test_pkc_find PUBLIC ${SIMAGEPC_LINK_LIBRARIES})
target_include_directories(test_pkc_find PUBLIC ${SIMAGEPC_INCLUDE_DIRS})


