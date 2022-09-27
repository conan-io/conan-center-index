cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

if(MSVC)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS -D_CRT_NONSTDC_NO_WARNINGS)
endif()

find_package(JPEG REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE JPEG::JPEG)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)

if(BUILD_TRANSUPP)
    add_executable(test_transupp test_transupp.c ${LIBJPEG_RES_DIR}/transupp.c)
    target_link_libraries(test_transupp PRIVATE JPEG::JPEG)
    target_compile_features(test_transupp PRIVATE c_std_99)
endif()
