# Simplified replacement for https://github.com/RainerKuemmerle/g2o/blob/master/cmake_modules/FindSuiteSparse.cmake

if (G2O_USE_CHOLMOD)
    find_package(CHOLMOD REQUIRED CONFIG)
    add_library(SuiteSparse::Partition ALIAS SuiteSparse::CHOLMOD)
    set(SuiteSparse_FOUND TRUE)
    set(SuiteSparse_CHOLMOD_FOUND TRUE)
endif()
