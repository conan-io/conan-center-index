cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX C)

find_package(OpenMP REQUIRED)

message("OpenMP_FOUND: ${OpenMP_CXX_FOUND}")
message("OpenMP_VERSION: ${OpenMP_VERSION}")
message("OpenMP_C_FOUND: ${OpenMP_CXX_FOUND}")
message("OpenMP_CXX_FOUND: ${OpenMP_CXX_FOUND}")
message("OpenMP_CXX_VERSION: ${OpenMP_CXX_VERSION}")
message("OpenMP_CXX_SPEC_DATE: ${OpenMP_CXX_SPEC_DATE}")
message("OpenMP_CXX_INCLUDE_DIRS: ${OpenMP_CXX_INCLUDE_DIRS}")
message("OpenMP_CXX_LIB_NAMES: ${OpenMP_CXX_LIB_NAMES}")
message("OpenMP_CXX_LIBRARIES: ${OpenMP_CXX_LIBRARIES}")
message("OpenMP_CXX_FLAGS: ${OpenMP_CXX_FLAGS}")
message("OpenMP_omp_LIBRARY: ${OpenMP_omp_LIBRARY}")

if(NOT DEFINED OpenMP_CXX_SPEC_DATE)
    message(FATAL_ERROR "FindOpenMP.cmake did not set all variables correctly.")
endif()

add_executable(test_package_cxx test_package.cpp)
target_link_libraries(test_package_cxx OpenMP::OpenMP_CXX)

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c OpenMP::OpenMP_C)

# Using PkgConfigDeps output to test the configuration exported by package_info().
# This is not a recommended or conventional way to use OpenMP.
find_package(PkgConfig REQUIRED)
pkg_check_modules(openmp REQUIRED IMPORTED_TARGET openmp)
add_executable(test_package_pkgconfig test_package.c)
target_link_libraries(test_package_pkgconfig PkgConfig::openmp)
