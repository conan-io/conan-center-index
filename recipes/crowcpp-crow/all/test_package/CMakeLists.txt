cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Crow REQUIRED)

option(CROW_AMALGAMATION "CROW IS DEPLOYED AS AMALGAMATION" ON)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Crow::Crow)

if(CROW_AMALGAMATION)
    target_compile_definitions(${PROJECT_NAME} PRIVATE CROW_AMALGAMATION)
endif(CROW_AMALGAMATION)
unset(CROW_AMALGAMATION CACHE)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
