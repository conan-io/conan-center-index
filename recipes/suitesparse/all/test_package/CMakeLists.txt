cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(SuiteSparse REQUIRED COMPONENTS
    suitesparse_config amd btf camd ccolamd colamd cxsparse ldl mongoose
    klu umfpack cholmod rbio spex paru graphblas lagraph
)

add_executable(test_package main.c)
target_link_libraries(test_package PRIVATE
    SuiteSparse::SuiteSparseConfig
    SuiteSparse::AMD
    SuiteSparse::BTF
    SuiteSparse::CAMD
    SuiteSparse::CCOLAMD
    SuiteSparse::COLAMD
    SuiteSparse::CXSparse
    SuiteSparse::LDL
    SuiteSparse::Mongoose
    SuiteSparse::KLU
    SuiteSparse::UMFPACK
    SuiteSparse::CHOLMOD
    SuiteSparse::RBio
    SuiteSparse::SPEX
    SuiteSparse::GraphBLAS
    SuiteSparse::LAGraph
)

add_executable(test_package_cpp main.cpp)
target_link_libraries(test_package_cpp PRIVATE
    SuiteSparse::SPQR
    SuiteSparse::ParU
    SuiteSparse::Mongoose
)
