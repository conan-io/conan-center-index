cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(crashpad REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE crashpad::client)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

if(APPLE)
    find_library(COREFOUNDATION_FRAMEWORK CoreFoundation)
    find_library(FOUNDATION_FRAMEWORK Foundation)
    find_library(IOKIT_FRAMEWORK IOKit)
    find_library(SECURITY_FRAMEWORK Security)
    find_library(APPSERVICES_FRAMEWORK ApplicationServices)
    find_library(BSM_LIBRARY bsm)

    target_link_libraries(${PROJECT_NAME}
        PRIVATE
            ${COREFOUNDATION_FRAMEWORK}
            ${FOUNDATION_FRAMEWORK}
            ${IOKIT_FRAMEWORK}
            ${SECURITY_FRAMEWORK}
            ${APPSERVICES_FRAMEWORK}
            ${BSM_LIBRARY}
    )
endif()
