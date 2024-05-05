cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(exiv2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} exiv2lib)

if(${exiv2_VERSION} VERSION_GREATER_EQUAL "0.28.0")
	target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
