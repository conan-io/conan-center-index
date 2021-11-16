cmake_minimum_required(VERSION 3.13)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(certify REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE certify::certify)
target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
