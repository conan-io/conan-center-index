cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(ethash REQUIRED CONFIG)

set(ETHASH_TARGETS ethash::keccak)
if (TARGET ethash::ethash)
    list(APPEND ETHASH_TARGETS ethash::ethash)
endif()
if (TARGET ethash::global-context)
    list(APPEND ETHASH_TARGETS ethash::global-context)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${ETHASH_TARGETS})
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 14)
