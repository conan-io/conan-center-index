cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(dlib REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE dlib::dlib)

if(dlib_VERSION VERSION_GREATER_EQUAL 19.24.2)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()
