cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

find_package(stc REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE stc::stc)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
if(${stc_VERSION} STREQUAL "1.0.0-rc1")
    target_compile_definitions(${PROJECT_NAME} PRIVATE STC_VERSION=1)
elseif(${stc_VERSION} VERSION_GREATER_EQUAL "3.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE STC_VERSION=3)
endif()
