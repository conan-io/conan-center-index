# Simplified replacement for https://github.com/ceres-solver/ceres-solver/blob/2.2.0/cmake/FindSuiteSparse.cmake

find_package(CHOLMOD REQUIRED CONFIG)
find_package(SPQR REQUIRED CONFIG)
find_package(METIS CONFIG)

add_library(SuiteSparse::Partition ALIAS SuiteSparse::CHOLMOD)

set(SuiteSparse_FOUND TRUE)
