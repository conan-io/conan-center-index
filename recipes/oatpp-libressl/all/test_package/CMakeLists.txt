cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(oatpp-libressl REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE oatpp::oatpp-libressl)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
