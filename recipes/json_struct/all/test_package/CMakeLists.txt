cmake_minimum_required(VERSION 3.15)

project(JsonStructTester
        DESCRIPTION "Tester package for json_struct"
        LANGUAGES C CXX)

find_package(json_struct REQUIRED)

add_executable(${PROJECT_NAME} main.cpp)

target_link_libraries(${PROJECT_NAME} json_struct::json_struct)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_14)
