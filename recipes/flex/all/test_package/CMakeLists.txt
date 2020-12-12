cmake_minimum_required(VERSION 3.1)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

find_package(FLEX REQUIRED)

flex_target(flex_scanner basic_nr.l "${PROJECT_BINARY_DIR}/basic_nr.cpp")

add_executable(${PROJECT_NAME} basic_nr.cpp ${FLEX_flex_scanner_OUTPUTS})
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
if(FLEX_VERSION STREQUAL "2.5.39")   # 2.5.39 is the only 2.5.x version released on Github
    target_compile_definitions(${PROJECT_NAME} PUBLIC FLEX_25)
endif()
