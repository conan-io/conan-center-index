cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(fcftest REQUIRED CONFIG)

include(FetchContent)
if(NOT FCFTEST_VERSION)
    set(FCFTEST_VERSION "1.2.5")
endif()

FetchContent_Declare(
    fcftest_source
    URL "https://github.com/fcf-framework/fcfTest/archive/refs/tags/v${FCFTEST_VERSION}.zip"
)

FetchContent_GetProperties(fcftest_source)
if(NOT fcftest_source_POPULATED)
    FetchContent_Populate(fcftest_source)

    file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/include/fcfTest")

    file(COPY "${fcftest_source_SOURCE_DIR}/test.hpp" DESTINATION "${CMAKE_CURRENT_BINARY_DIR}/include/fcfTest")

    include_directories(${CMAKE_CURRENT_BINARY_DIR}/include)

    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}")

    add_subdirectory(${fcftest_source_SOURCE_DIR} ${fcftest_source_BINARY_DIR})
endif()

# === ИСПРАВЛЕНИЕ ОШИБКИ ИНКЛЮДА ===
# Находим таргет ваших внутренних тестов библиотеки.
# Судя по путям, в вашем add_subdirectory создается исполняемый файл. 
# Замените "fcftest-tests" на точное имя таргета из вашего внутреннего CMakeLists.txt
if(TARGET fcftest-tests)
    # Линкуем к вашим тестам сгенерированный Conan пакет fcftest::fcftest.
    # Он автоматически пропишет правильные пути поиска хедера (<fcfTest/test.hpp>)
    target_link_libraries(fcftest-tests PRIVATE fcftest::fcftest)
endif()

# Стандартная заглушка приложения для самого Conan Center Index
add_executable(test_package main.cpp)
target_link_libraries(test_package PRIVATE fcftest::fcftest)

