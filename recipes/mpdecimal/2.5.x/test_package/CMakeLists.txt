cmake_minimum_required(VERSION 3.15)
project(test_package)

enable_testing()

# This is a non-official mpdecimal module!
find_package(mpdecimal REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE mpdecimal::libmpdecimal)
add_test(NAME test_package COMMAND test_package 10 13)

if(MPDECIMAL_CXX)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    set_propertY(TARGET ${PROJECT_NAME}_cpp PROPERTY CXX_STANDARD 11)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE mpdecimal::libmpdecimal++)
    add_test(NAME test_package_cpp COMMAND test_package_cpp 10 13)
endif()
