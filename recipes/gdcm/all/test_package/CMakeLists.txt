cmake_minimum_required(VERSION 3.9.2)
project(test_package)

if(NOT DEFINED CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 11)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(GDCM REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
include(${GDCM_USE_FILE})
target_link_libraries(${PROJECT_NAME} gdcmMSFF)
