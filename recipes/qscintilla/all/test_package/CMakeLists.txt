cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(QScintilla REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

if(QT_VERSION VERSION_GREATER_EQUAL "6.0.0")
    find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets PrintSupport CONFIG)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets Qt6::PrintSupport)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
elseif(QT_VERSION VERSION_GREATER_EQUAL "5.0.0")
    find_package(Qt5 REQUIRED COMPONENTS Core Gui Widgets PrintSupport CONFIG)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt5::Core Qt5::Gui Qt5::Widgets Qt5::PrintSupport)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
else()
    message(FATAL_ERROR "Qt < 5 is not supported by this recipe")
endif()

target_link_libraries(${PROJECT_NAME} PRIVATE QScintilla::QScintilla)

if(NOT WIN32)
    # Must compile with "-fPIC" since Qt was built with -reduce-relocations.
    target_compile_options(${PROJECT_NAME} PRIVATE -fPIC)
endif()
