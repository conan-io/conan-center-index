cmake_minimum_required(VERSION 3.3)

project(DocGenTestConan VERSION 0.0.1)

find_package(Doxygen REQUIRED)
find_package(DocGen REQUIRED)
configure_doxygen(
    MAINPAGE README.md
    INPUT "src" "include"
    STRIP_INC_PATH "include")

add_executable(${PROJECT_NAME} src/${PROJECT_NAME})
target_include_directories(${PROJECT_NAME} PRIVATE include)
