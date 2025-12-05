cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(pfr_non_boost REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE pfr_non_boost::pfr_non_boost)

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)

# target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
# add_compile_definitions("PFR_USE_CPP17=1")

# target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
# add_compile_definitions("PFR_CORE_NAME_ENABLED=1")