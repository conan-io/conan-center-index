cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX C)

find_package(OpenMP MODULE REQUIRED)

message("OpenMP_FOUND: ${OpenMP_CXX_FOUND}")
message("OpenMP_CXX_FOUND: ${OpenMP_CXX_FOUND}")
message("OpenMP_CXX_VERSION: ${OpenMP_CXX_VERSION}")
message("OpenMP_CXX_SPEC_DATE: ${OpenMP_CXX_SPEC_DATE}")
message("OpenMP_CXX_INCLUDE_DIRS: ${OpenMP_CXX_INCLUDE_DIRS}")
message("OpenMP_INCLUDE_DIRS: ${OpenMP_CXX_INCLUDE_DIRS}")

if(NOT DEFINED OpenMP_C_INCLUDE_DIRS)
    message(FATAL_ERROR "OpenMP_C_INCLUDE_DIRS is not defined")
endif()
if(NOT DEFINED OpenMP_CXX_INCLUDE_DIRS)
    message(FATAL_ERROR "OpenMP_CXX_INCLUDE_DIRS is not defined")
endif()

add_executable(test_package_cxx test_package.cpp)
target_link_libraries(test_package_cxx OpenMP::OpenMP_CXX)

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c OpenMP::OpenMP_C)
