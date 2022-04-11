cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(avcpp CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
if (TARGET avcpp::avcpp)
    target_link_libraries(${PROJECT_NAME} avcpp::avcpp)
else()
    target_link_libraries(${PROJECT_NAME} avcpp::avcpp-static)
endif()
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
