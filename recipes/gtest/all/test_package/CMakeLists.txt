cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(GTest REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE GTest::gtest)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(WITH_MAIN)
    target_link_libraries(${PROJECT_NAME} PRIVATE GTest::gtest_main)
    if(WITH_GMOCK)
        target_link_libraries(${PROJECT_NAME} PRIVATE GTest::gmock_main)
    endif()
else()
    target_sources(${PROJECT_NAME} PRIVATE main.cpp)
endif()

if(WITH_GMOCK)
    target_link_libraries(${PROJECT_NAME} PRIVATE GTest::gmock)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_GMOCK)
endif()
