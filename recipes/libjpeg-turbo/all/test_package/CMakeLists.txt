cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES C)

find_package(libjpeg-turbo REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET libjpeg-turbo::jpeg)
    target_link_libraries(${PROJECT_NAME} PRIVATE libjpeg-turbo::jpeg)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE libjpeg-turbo::jpeg-static)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
