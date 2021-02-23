cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(tsl-array-hash REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} tsl::array_hash)
# Library works with C++11, but std::string_view features are also provided if C++17
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
