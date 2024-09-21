cmake_minimum_required(VERSION 3.15)
project(test_DrLibs LANGUAGES CXX)
find_package(dr_libs REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE dr_libs::dr_libs)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
