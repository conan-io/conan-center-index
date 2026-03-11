cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(opentelemetry-cpp REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE opentelemetry-cpp::opentelemetry-cpp)

if (NOT DEFINED OPENTELEMETRY_CPP_LIBRARIES)
    message(FATAL_ERROR "OPENTELEMETRY_CPP_LIBRARIES is not defined and is expected")
endif()

if (NOT DEFINED OPENTELEMETRY_CPP_INCLUDE_DIRS)
    message(FATAL_ERROR "OPENTELEMETRY_CPP_INCLUDE_DIRS is not defined and is expected")
endif()

message("OPENTELEMETRY_CPP_LIBRARIES: ${OPENTELEMETRY_CPP_LIBRARIES}")
message("OPENTELEMETRY_CPP_INCLUDE_DIRS: ${OPENTELEMETRY_CPP_INCLUDE_DIRS}")
