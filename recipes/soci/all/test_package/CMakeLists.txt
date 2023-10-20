cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(SOCI REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET SOCI::soci_core_static)
    target_link_libraries(${PROJECT_NAME} SOCI::soci_core_static)
else()
    target_link_libraries(${PROJECT_NAME} SOCI::soci_core)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
