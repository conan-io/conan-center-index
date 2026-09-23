cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

if(NOT DEFINED QUAZIP_QT_MAJOR_VERSION)
    set(QUAZIP_QT_MAJOR_VERSION 5)
endif()

find_package(QuaZip-Qt${QUAZIP_QT_MAJOR_VERSION} REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE QuaZip::QuaZip)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
# Must compile with "-fPIC" since Qt was built with -reduce-relocations.
target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)
