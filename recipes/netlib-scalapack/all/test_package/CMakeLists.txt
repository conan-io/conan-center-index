cmake_minimum_required(VERSION 3.15)
project(test_package_netlib_scalapack LANGUAGES Fortran)

find_package(netlib-scalapack CONFIG REQUIRED)

add_executable(test_package test_package.f90)
target_link_libraries(test_package PRIVATE netlib-scalapack::netlib-scalapack)
