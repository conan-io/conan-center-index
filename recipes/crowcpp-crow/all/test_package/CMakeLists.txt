cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(crow REQUIRED)

option(CROW_AMALGAMATION "CROW IS DEPLOYED AS AMALGAMATION" ON)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} crow::crow)

if(CROW_AMALGAMATION)
    target_compile_definitions(${PROJECT_NAME} PRIVATE CROW_AMALGAMATION)
endif(CROW_AMALGAMATION)
unset(CROW_AMALGAMATION CACHE)

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
