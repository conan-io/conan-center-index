cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(scn REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET scn::scn-header-only)
    target_link_libraries(${PROJECT_NAME} PRIVATE scn::scn-header-only)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE scn::scn)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
