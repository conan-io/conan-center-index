cmake_minimum_required(VERSION 3.21.0)
project(pingpong LANGUAGES CXX)
set(TARGET pingpong)

find_package(Qt6 COMPONENTS Core REQUIRED)

set(CMAKE_AUTOMOC ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON)

enable_testing()

set(SOURCES
    main.cpp
)

add_executable(${TARGET} ${SOURCES})
target_link_libraries(${TARGET} Qt6::Core)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
target_precompile_headers(${TARGET} PRIVATE Precompiled.h)
