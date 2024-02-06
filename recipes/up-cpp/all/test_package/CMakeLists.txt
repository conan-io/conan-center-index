cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(up-cpp REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PUBLIC up-cpp::up-cpp)

target_include_directories(${PROJECT_NAME} PRIVATE  
                           ${up-cpp_INCLUDE_DIRS}
                           ${up-cpp_INCLUDE_DIRS}/up-core-api
                           
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
