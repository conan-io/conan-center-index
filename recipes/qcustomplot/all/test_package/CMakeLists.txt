cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(qcustomplot REQUIRED CONFIG)
find_package(Qt5 QUIET COMPONENTS Core Widgets)
find_package(Qt6 QUIET COMPONENTS Core Widgets)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE qcustomplot::qcustomplot)

if (Qt5_FOUND)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt5::Core Qt5::Widgets)
elseif(Qt6_FOUND)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Core Qt6::Widgets)
else()
    message(FATAL_ERROR "Could not find Qt5 or Qt6. Please, check your Conan requirements.")
endif()
