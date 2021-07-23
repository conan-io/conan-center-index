cmake_minimum_required(VERSION 3.10)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE CONAN_PKG::libbasisu)
set_target_properties(${PROJECT_NAME} PROPERTIES
    CXX_STANDARD 11
    CXX_STANDARD_REQUIRED ON
)
