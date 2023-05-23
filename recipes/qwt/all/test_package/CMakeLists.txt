cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(qwt REQUIRED CONFIG)
find_package(Qt5 REQUIRED Core CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE qwt::qwt Qt5::Core)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(NOT WIN32)
    # Must compile with "-fPIC" since Qt was built with -reduce-relocations.
    target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)
endif()
