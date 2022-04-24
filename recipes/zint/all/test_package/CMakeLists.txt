cmake_minimum_required(VERSION 3.1)
project(test_package C)

option(ZINT_WITH_QT "Zint has been built with Qt support")
if(ZINT_WITH_QT)
    enable_language(CXX)
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Zint REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE Zint::Zint)

if(ZINT_WITH_QT)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE Zint::QZint)
endif()
