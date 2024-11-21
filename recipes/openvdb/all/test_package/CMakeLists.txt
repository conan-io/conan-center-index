cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(OpenVDB REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE OpenVDB::openvdb)
if (OpenVDB_VERSION VERSION_GREATER_EQUAL "10.0.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
endif()
