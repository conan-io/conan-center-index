cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)

find_package(qcustomplot REQUIRED CONFIG)
target_link_libraries(${PROJECT_NAME} PRIVATE qcustomplot::qcustomplot)

if(QT_VERSION VERSION_GREATER_EQUAL "6.0.0")
    find_package(Qt6 COMPONENTS Core Widgets REQUIRED CONFIG)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Core Qt6::Widgets)
    target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_17)
elseif(QT_VERSION VERSION_GREATER_EQUAL "5.0.0")
    find_package(Qt5 COMPONENTS Core Widgets REQUIRED CONFIG)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt5::Core Qt5::Widgets)
    target_compile_features(${PROJECT_NAME} PUBLIC cxx_std_11)
else()
    message(FATAL_ERROR "Qt < 5 not yet supported in this recipe")
endif()
