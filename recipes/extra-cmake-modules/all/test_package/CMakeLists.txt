cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)


find_package(ECM REQUIRED NO_MODULE)
# ECMConfig.cmake must derive ECM_PREFIX from its own location: an absolute build prefix
# looks right on the build machine (Conan builds into the final package folder) and only
# breaks once the package is downloaded somewhere else
file(STRINGS "${ECM_DIR}/ECMConfig.cmake" _ecm_prefix_line REGEX "^set\\(ECM_PREFIX ")
if(NOT _ecm_prefix_line MATCHES "^set\\(ECM_PREFIX \"\\\${PACKAGE_PREFIX_DIR}\"\\)$")
    message(FATAL_ERROR "ECMConfig.cmake hard-codes ECM_PREFIX: ${_ecm_prefix_line}")
endif()
list(APPEND CMAKE_MODULE_PATH ${ECM_MODULE_PATH})
include(ECMGenerateHeaders)

add_library(MyLib INTERFACE)
target_include_directories(MyLib INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}")
ecm_generate_headers(
    MyLib_FORWARDING_HEADERS
    HEADER_NAMES Foo
    REQUIRED_HEADERS MyLib_HEADERS
)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE MyLib)
