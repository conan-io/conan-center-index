cmake_minimum_required(VERSION 3.5)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(mdspan REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE std::mdspan)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_14)
