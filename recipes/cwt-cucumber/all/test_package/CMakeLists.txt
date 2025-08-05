cmake_minimum_required(VERSION 3.15)
project(cwt-cucumber-test)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)

find_package(cwt-cucumber REQUIRED)

set(target test_package)

add_executable(${target} test_package.cpp)

target_link_libraries(${target} cwt::cucumber)
