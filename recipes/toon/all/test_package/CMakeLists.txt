cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(PkgConfig REQUIRED)
pkg_check_modules(TooN REQUIRED IMPORTED_TARGET TooN)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::TooN)
if (WITH_LAPACK)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "WITH_LAPACK")
endif ()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
