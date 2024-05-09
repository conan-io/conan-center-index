cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(OpenImageIO REQUIRED CONFIG)
find_package(fmt REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE OpenImageIO::OpenImageIO
                                              OpenImageIO::OpenImageIO_Util
                                              fmt::fmt)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
