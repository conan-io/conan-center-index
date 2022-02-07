cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(cryptopp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET cryptopp-shared)
    target_link_libraries(${PROJECT_NAME} cryptopp-shared)
else()
    target_link_libraries(${PROJECT_NAME} cryptopp-static)
endif()
