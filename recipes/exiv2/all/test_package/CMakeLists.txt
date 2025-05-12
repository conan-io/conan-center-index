cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(exiv2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE exiv2lib)

if(${exiv2_VERSION} VERSION_GREATER_EQUAL "0.28.0")
	target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
