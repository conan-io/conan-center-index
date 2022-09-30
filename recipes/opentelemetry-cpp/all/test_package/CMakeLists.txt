cmake_minimum_required(VERSION 3.4)

project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(opentelemetry-cpp REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE ${OPENTELEMETRY_CPP_INCLUDE_DIRS})
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE ${OPENTELEMETRY_CPP_LIBRARIES})
target_compile_features(${CMAKE_PROJECT_NAME} PRIVATE cxx_std_11)
