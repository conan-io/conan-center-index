cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

enable_testing()

find_package(cxxopts REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cxxopts::cxxopts)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

if(cxxopts_VERSION VERSION_LESS "3.1.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE CXXOPTS_OLD_EXCEPTIONS)
endif()

add_test(NAME ${PROJECT_NAME} COMMAND ${PROJECT_NAME} -f 41 --bar baria --baz)
if(WITH_UNICODE)
    # This will fail if it was not enabled in the package https://github.com/jarro2783/cxxopts#unrecognised-arguments
    add_test(NAME unicode COMMAND ${PROJECT_NAME} -f 41 --bar baria --baz -q quxis)
endif()
