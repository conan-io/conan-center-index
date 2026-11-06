cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(nepdate REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
if(NEPDATE_TEST_PATRO)
    # nepdate::patro alone: the core headers it includes must come through it
    target_link_libraries(${PROJECT_NAME} PRIVATE nepdate::patro)
    target_compile_definitions(${PROJECT_NAME} PRIVATE NEPDATE_TEST_PATRO)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE nepdate::nepdate)
endif()
