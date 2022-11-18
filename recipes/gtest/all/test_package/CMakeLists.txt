cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(GTest REQUIRED)

if(WITH_MAIN)
    add_executable(${PROJECT_NAME} test_package.cpp)
else()
    add_executable(${PROJECT_NAME} main.cpp test_package.cpp)
endif()

if(WITH_MAIN)
    target_link_libraries(${PROJECT_NAME} PRIVATE GTest::gtest GTest::gtest_main)
    if(WITH_GMOCK)
        target_link_libraries(${PROJECT_NAME} PRIVATE GTest::gmock GTest::gmock_main)
    endif()
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE GTest::gtest)
    if(WITH_GMOCK)
        target_link_libraries(${PROJECT_NAME} PRIVATE GTest::gmock)
    endif()
endif()
if(WITH_GMOCK)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_GMOCK)
endif()


target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
