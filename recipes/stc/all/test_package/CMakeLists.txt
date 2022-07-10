cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(stc REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} stc::stc)
if(${stc_VERSION} STREQUAL "1.0.0-rc1")
    target_compile_definitions(${PROJECT_NAME} PRIVATE STC_VERSION=1)
elseif(${stc_VERSION} VERSION_GREATER_EQUAL "3.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE STC_VERSION=3)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD_REQUIRED ON)
