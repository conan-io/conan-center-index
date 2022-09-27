cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(MSVC)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS -D_CRT_NONSTDC_NO_WARNINGS)
endif()

find_package(JPEG REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE JPEG::JPEG)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)

add_executable(test_transupp ../test_package/test_transupp.c "${CONAN_LIBJPEG_ROOT}/res/transupp.c")
target_link_libraries(test_transupp PRIVATE JPEG::JPEG)
target_compile_features(test_transupp PRIVATE c_std_99)
