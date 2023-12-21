cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(lunasvg REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE lunasvg::lunasvg)
if (lunasvg_VERSION VERSION_LESS_EQUAL "2.3.2")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
