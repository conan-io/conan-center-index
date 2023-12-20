cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(zserio REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE zserio::ZserioCppRuntime)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

# check that ZSERIO_JAR_FILE exists
if (NOT DEFINED ENV{ZSERIO_JAR_FILE})
    message(FATAL_ERROR "ZSERIO_JAR_FILE in not defined!")
endif ()
if (NOT EXISTS $ENV{ZSERIO_JAR_FILE})
    message(FATAL_ERROR "ZSERIO_JAR_FILE '$ENV{ZSERIO_JAR_FILE}' does not exist!")
endif ()
